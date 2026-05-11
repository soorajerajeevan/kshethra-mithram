

let poojaCounter = 0;
let retailCounter = 0;
let poojas = [];
let retailItems = [];
let devotees = [];
let devoteeSelectTS = null;
let selectedDevotee = {};
let familyMembers = [];
let nakshathrams = [];
let tomSelectInstances = [];

function poojaLabel(p) { return `${p.id} - ${p.malayalam_name || p.name}`; }
function devoteeLabel(d) { return `${d.full_name} (${d.family_name || ''}) - ${d.phone || 'No phone'}`; }

document.addEventListener(
    'DOMContentLoaded',
    async function () {

        fontManager = new FontSizeManager();

        await loadBillingFormData();

        updateEditDevoteeButton();
    }
);

async function loadBillingFormData() {
    try {
        const response = await fetch('/billing/api/billing-form-data');
        const data = await response.json();
        poojas = data.poojas || [];
        retailItems = data.retailItems || [];
        devotees = data.devotees || [];
        nakshathrams = data.nakshathrams || [];
        devotees = devotees.map(d => ({ ...d, display_name: devoteeLabel(d) }));

        initializeSearchables();
        buildQuickRetailItems();
        addPoojaItem();
    } catch (error) {
        console.error('Error loading billing form data:', error);
    }
}


function initSearchableSelect(selector, options = {}) {
    const el = document.querySelector(selector);
    if (!el || typeof TomSelect === 'undefined') return null;
    if (el.tomselect) return el.tomselect;
    return new TomSelect(el, {
        maxOptions: 50,
        closeAfterSelect: true,
        ...options
    });
}

function initializeSearchables() {

    // #Devotee Dropdown
    devoteeSelectTS = initSearchableSelect('#devotee_id', {
        placeholder: 'Type devotee name / ID / phone',
        options: devotees,
        valueField: 'id',
        labelField: 'display_name',
        searchField: ['full_name', 'phone', 'family_name'],
        create: function (input) {
            const name = (input || '').trim();
            if (!name) return false;
            return {
                id: 0, // Temporary ID for new devotee
                display_name: `${name} (New devotee)`,
                full_name: name,
            };
        },
        onChange: function (id) {
            selectedDevotee = getSelectedPrimaryDevotee();
            document.getElementById('devotee_name').value = selectedDevotee.full_name;
            updateFamilyMemberOptions(id);
            updateEditDevoteeButton(id);
            if (id == 0) {
                toggleNewDevoteePhone(id);
            }
        }
    });
}

function getSelectedPrimaryDevotee() {
    const devoteeId = document.getElementById('devotee_id').value || '';
    if (!/^\d+$/.test(devoteeId)) return null;
    if (devoteeId == 0) {
        return {
            id: 0,
            full_name: document.getElementById('devotee_id').options[document.getElementById('devotee_id').selectedIndex].text.replace(' (New devotee)', '').trim(),
            nakshathram: '',
            family_members: [],
            phone: document.getElementById('new_devotee_phone').value.trim()
        };
    }
    return devotees.find(d => String(d.id) === String(devoteeId)) || null;
}

function updateFamilyMemberOptions(devoteeId) {
    if (selectedDevotee) {
        familyMembers = [{ name: selectedDevotee.full_name, nakshathram: selectedDevotee.nakshatra }];
        familyMembers.push(...selectedDevotee.family_members.map(m => ({ name: m.name, nakshathram: m.nakshathram })));
    }
    console.log("Refreshing family member options for all pooja rows. Family members:", familyMembers);
    Object.keys(tomSelectInstances)
        .filter(key => key.startsWith('family_'))
        .forEach(key => {
            const ts = tomSelectInstances[key];
            ts.clearOptions();

            familyMembers.forEach(m => {
                ts.addOption(m);
            });
            if (key === 'family_0' && selectedDevotee) {
                ts.setValue(selectedDevotee.full_name, false);
            }
        });
}


function toggleNewDevoteePhone(value) {
    const wrap = document.getElementById('newDevoteePhoneWrap');
    const phone = document.getElementById('new_devotee_phone');

    if (!wrap || !phone) return;
    const isNew = value == 0;
    if (isNew) {
        wrap.classList.remove('d-none');
        phone.required = true;
    } else {
        wrap.classList.add('d-none');
        phone.required = false;
        phone.value = '';
    }
}

function initPoojaRowSearchables(index) {
    const poojaSelector = `#pooja_service_${index}`;
    const familySelector = `#pooja_devotee_name_${index}`;
    const nakshSelector = `#pooja_nakshathram_${index}`;

    const poojaTs = initSearchableSelect(poojaSelector, {
        valueField: 'id',
        labelField: 'name',
        searchField: ['english_name', 'id', 'malayalam_name'],
        options: poojas,
        create: false,
        onChange: function () {
            updatePoojaPrice(index);
        }
    });

    const nakshTs = initSearchableSelect(nakshSelector, {
        valueField: 'malayalam_name',
        labelField: 'display_name',
        searchField: ['english_name', 'id', 'malayalam_name'],
        options: nakshathrams.map(n => ({ id: n.id, english_name: n.english_name, malayalam_name: n.malayalam_name, display_name: n.id + ' - ' + n.malayalam_name })),
        placeholder: 'Nakshathram',
        create: false
    });

    const familyTs = initSearchableSelect(familySelector, {
        valueField: 'name',
        labelField: 'name',
        searchField: ['name'],
        placeholder: 'Family member name',
        options: familyMembers,
        create: true,
        onChange: function () {
            prefillNakshathramFromFamily(index);
        }
    });
    if (poojaTs) {
        tomSelectInstances[`pooja_${index}`] = poojaTs;
    }
    if (nakshTs) {
        tomSelectInstances[`nakshathram_${index}`] = nakshTs;
    }
    if (familyTs) {
        tomSelectInstances[`family_${index}`] = familyTs;
    }
}

function updateEditDevoteeButton(id) {
    const btn = document.getElementById('editDevoteeBtn');
    if (!btn && !id) return;
    if (id > 0) {
        btn.href = `/devotees/${id}/edit`;
        btn.classList.remove('disabled');
        btn.setAttribute('aria-disabled', 'false');
    } else {
        btn.href = '#';
        btn.classList.add('disabled');
        btn.setAttribute('aria-disabled', 'true');
    }
}

function prefillNakshathramFromFamily(index) {
    const nakshSelect = tomSelectInstances[`nakshathram_${index}`];
    const familySelect = tomSelectInstances[`family_${index}`];
    if (!nakshSelect || !familySelect) return;
    const familyMemberName = familySelect.getValue();
    nakshSelect.setValue(''); // Clear nakshathram when family member change
    nakshSelect.setValue(familyMembers.find(m => m.name === familyMemberName)?.nakshathram || '', true);
}

function buildQuickRetailItems() {
    const container = document.getElementById('quickRetailItems');
    if (!container) return;
    container.innerHTML = retailItems.map(item => `
        <button type="button" class="btn btn-outline-primary"
                onclick="quickAddRetail(${item.id})">
            <div class="fw-semibold">${item.name}</div>
            <div class="small">Rs.${(item.selling_price).toFixed(2)}</div>
        </button>
    `).join('');
}

function addPoojaItem() {
    const container = document.getElementById('poojaItems');
    const itemDiv = document.createElement('div');
    itemDiv.className = 'row g-2 mb-2 pooja-item';
    itemDiv.id = `pooja_item_${poojaCounter}`;

    itemDiv.innerHTML = `
        <div class="col-md-2">
            <select name="pooja_service_${poojaCounter}" id="pooja_service_${poojaCounter}" class="form-select form-select-sm">
                <option value="">Select pooja</option>
                ${poojas.map(p => `<option value="${p.id}" data-price="${p.default_price}">${poojaLabel(p)}|||${p.english_name || ''}</option>`).join('')}
            </select>
        </div>
        <div class="col-md-2">
            <select name="pooja_devotee_name_${poojaCounter}" id="pooja_devotee_name_${poojaCounter}" class="form-select form-select-sm" required></select>
        </div>
        <div class="col-md-2">
            <select name="pooja_nakshathram_${poojaCounter}" id="pooja_nakshathram_${poojaCounter}" class="form-select form-select-sm" required></select>
        </div>
        <div class="col-md-2"><input type="date" name="pooja_date_${poojaCounter}" id="pooja_date_${poojaCounter}" class="form-control form-control-sm" required></div>
       
        <div class="col-md-1"><input type="number" name="pooja_quantity_${poojaCounter}" id="pooja_quantity_${poojaCounter}" class="form-control form-control-sm" value="1" step="1" min="1" onchange="calculateTotal()" required></div>
        <div class="col-md-1"><input type="number" name="pooja_price_${poojaCounter}" id="pooja_price_${poojaCounter}" class="form-control form-control-sm" step="1" min="0" placeholder="Price" onchange="calculateTotal()" required></div>
         <div class="col-md-1 d-flex justify-content-center">        
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" role="switch" name="add_to_booking_${poojaCounter}"  id="pooja_booking_toggle_${poojaCounter}" >
            </div>    
        </div>
        <div class="col-md-1"><button type="button" class="btn btn-sm btn-danger" onclick="removeItem('pooja_item_${poojaCounter}', 'pooja')"><i class="bi bi-x"></i></button></div>
    `;

    container.appendChild(itemDiv);
    initPoojaRowSearchables(poojaCounter);
    document.getElementById('pooja_date_' + poojaCounter).value = getToday();
    poojaCounter++;
    document.getElementById('poojaCount').value = poojaCounter;

    itemDiv.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                addPoojaItem();
                const nextInput = document.getElementById(`pooja_service_${poojaCounter - 1}`);
                if (nextInput && nextInput.tomselect) {
                    nextInput.tomselect.focus();
                }
            }
        });
    });
}

function addRetailItem(preselectedItemId = null) {
    const container = document.getElementById('retailItems');
    const itemDiv = document.createElement('div');
    itemDiv.className = 'row g-2 mb-2 retail-item';
    itemDiv.id = `retail_item_${retailCounter}`;
    itemDiv.innerHTML = `
        <div class="col-md-5">
            <select name="retail_item_${retailCounter}" id="retails_select_${retailCounter}" class="form-select form-select-sm retail-select" data-index="${retailCounter}" onchange="updateRetailPrice(${retailCounter})"></select>
        </div>
        <div class="col-md-2"><input type="number" name="retail_quantity_${retailCounter}" id="retail_quantity_${retailCounter}" class="form-control form-control-sm" value="1" step="1" min="1" onchange="updateRetailPrice(${retailCounter}); calculateTotal()"></div>
        <div class="col-md-4"><input type="number" name="retail_price_${retailCounter}" id="retail_price_${retailCounter}" class="form-control form-control-sm" placeholder="Price" onchange="calculateTotal()" disabled></div>
        <div class="col-md-1"><button type="button" class="btn btn-sm btn-danger" onclick="removeItem('retail_item_${retailCounter}', 'retail')"><i class="bi bi-x"></i></button></div>
    `;
    container.appendChild(itemDiv);
    // Initialize retail item select with options
    const retailsTs = initSearchableSelect(`#retails_select_${retailCounter}`, {
        valueField: 'id',
        labelField: 'name',
        options: retailItems,
        create: false
    });
    tomSelectInstances[`retail_${retailCounter}`] = retailsTs;

    console.log('Initializing retail item select for index:', retailItems, 'preselectedItemId:', preselectedItemId, '# : Retails TS : ', retailsTs);

    if (preselectedItemId) {
        retailsTs.setValue(String(preselectedItemId));
    }
    retailCounter++;
    document.getElementById('retailCount').value = retailCounter;
}

function quickAddRetail(itemId) {
    let updated = false;
    document.querySelectorAll('.retail-item').forEach(item => {
        if (updated) return;
        const index = item.id.split('_')[2];
        const select = document.querySelector(`select[name="retail_item_${index}"]`);
        if (select && Number(select.value) === Number(itemId)) {
            const qtyInput = document.getElementById(`retail_quantity_${index}`);
            qtyInput.value = (parseFloat(qtyInput.value) || 0) + 1;
            updateRetailPrice(index);
            updated = true;
        }
    });
    if (!updated) {
        addRetailItem(itemId);
    }
    calculateTotal();
}

function updatePoojaPrice(index) {
    const select = document.getElementById(`pooja_service_${index}`);
    const priceInput = document.getElementById(`pooja_price_${index}`);
    if (select && select.value) {
        const selectedOption = poojas.find(p => p.id == select.value);
        const price = Number(selectedOption?.default_price || 0);
        priceInput.value = (price).toFixed(2);
    } else {
        priceInput.value = '';
    }
    calculateTotal();

    const toggle = document.getElementById(`pooja_booking_toggle_${index}`);
    toggle.checked = getAddToBookingDefault(select.value);
}

function getAddToBookingDefault(poojaId) {
    const pooja = poojas.find(p => String(p.id) === String(poojaId));
    return pooja ? pooja.add_to_booking : false;
}

function updateRetailPrice(index) {
    console.log('Updating retail price for index:', index);
    const select = document.getElementById(`retails_select_${index}`);
    const qtyInput = document.getElementById(`retail_quantity_${index}`);
    const priceInput = document.getElementById(`retail_price_${index}`);
    if (select.value) {
        const price = Number(retailItems.find(r => r.id == select.value)?.selling_price || 0);
        priceInput.value = (price * (parseFloat(qtyInput.value) || 0)).toFixed(2);
    } else {
        priceInput.value = '';
    }
    calculateTotal();
}

function removeItem(itemId, type) {
    document.getElementById(itemId).remove();
    calculateTotal();
}

window.calculateTotal = function () {
    console.log('Calculating total');
    let subtotal = 0;
    document.querySelectorAll('.pooja-item').forEach(item => {
        const index = item.id.split('_')[2];
        const qty = parseFloat(document.getElementById(`pooja_quantity_${index}`).value) || 0;
        const price = parseFloat(document.getElementById(`pooja_price_${index}`).value) || 0;
        subtotal += qty * price;
    });
    document.querySelectorAll('.retail-item').forEach(item => {
        const index = item.id.split('_')[2];
        const qty = parseFloat(document.getElementById(`retail_quantity_${index}`).value) || 0;
        const price = parseFloat(document.getElementById(`retail_price_${index}`).value) || 0;
        subtotal += qty * price;
    });
    const discountType = document.getElementById('discountType').value;
    const discountValue = parseFloat(document.getElementById('discountValue').value) || 0;
    let discount = discountType === 'percent' ? subtotal * (discountValue) : discountValue;
    const donation = parseFloat(document.getElementById('donation').value) || 0;
    const grandTotal = subtotal - discount + donation;
    document.getElementById('subtotalDisplay').textContent = `Rs.${subtotal.toFixed(2)}`;
    document.getElementById('discountDisplay').textContent = `-Rs.${discount.toFixed(2)}`;
    document.getElementById('grandTotalDisplay').textContent = `Rs.${grandTotal.toFixed(2)}`;
}

function updateCredit() {
    alert('Credit amount updated. Please ensure to select "Credit" as payment mode if you are applying credit to this bill.');
}

document.getElementById('discountValue').addEventListener('input', calculateTotal);
document.getElementById('discountType').addEventListener('change', calculateTotal);
document.getElementById('donation').addEventListener('input', calculateTotal);

// Function to populate existing bill items when editing
function populateExistingBill() {
    if (!isBillEdit || !existingBill || !existingBill.items) return;

    const bill = existingBill;

    // Set discount and donation values
    if (bill.discount_value) {
        const discountType = bill.discount_type || 'amount';
        document.getElementById('discountType').value = discountType;
        document.getElementById('discountValue').value = bill.discount_value;
    }
    if (bill.donation_amount) {
        document.getElementById('donation').value = bill.donation_amount;
    }

    // Separate items into poojas and retail
    const poojaItemsToAdd = bill.items.filter(item => item.type === 'POOJA');
    const retailItemsToAdd = bill.items.filter(item => item.type === 'RETAIL');

    // Add pooja items
    poojaItemsToAdd.forEach(item => {
        addPoojaItem();
        const index = poojaCounter - 1;

        // Extract pooja info from item name (format: "Pooja Name for Family Member (Nakshathram)")
        const parts = item.name.match(/^(.+?)(?: for (.+?))?(?: \((.+?)\))?$/);
        const familyMember = parts ? parts[2] : '';
        const nakshathram = parts ? parts[3] : '';

        // Use item.id (service ID) to find the pooja directly - much more reliable
        const poojaService = poojas.find(p => p.id === item.id);

        if (poojaService) {
            const select = document.getElementById(`pooja_service_${index}`);
            if (select.tomselect) {
                select.tomselect.setValue(poojaService.id, false);
            } else {
                select.value = poojaService.id;
            }
            updatePoojaPrice(index);
        }

        // Set quantity
        document.getElementById(`pooja_quantity_${index}`).value = item.quantity;

        // Set custom price if different
        document.getElementById(`pooja_price_${index}`).value = item.unit_price.toFixed(2);

        // Set family member and nakshathram
        if (familyMember) {
            const familySelect = document.getElementById(`pooja_devotee_name_${index}`);
            if (familySelect.tomselect) {
                familySelect.tomselect.addOption({ value: familyMember, text: familyMember });
                familySelect.tomselect.setValue(familyMember, false);
            } else {
                familySelect.value = familyMember;
            }
        }
        if (nakshathram) {
            const nakshSelect = document.getElementById(`pooja_nakshathram_${index}`);
            if (nakshSelect.tomselect) {
                nakshSelect.tomselect.addOption({ value: nakshathram, text: nakshathram });
                nakshSelect.tomselect.setValue(nakshathram, false);
            } else {
                nakshSelect.value = nakshathram;
            }
        }
    });

    // Add retail items
    retailItemsToAdd.forEach(item => {
        addRetailItem();
        const index = retailCounter - 1;

        const select = document.querySelector(`select[name="retail_item_${index}"]`);
        const retailItem = retailItems.find(r => r.id === item.id);
        if (retailItem) {
            select.value = item.id;
        }

        document.getElementById(`retail_quantity_${index}`).value = item.quantity;
        document.getElementById(`retail_price_${index}`).value = item.unit_price.toFixed(2);
    });

    // Remove the default first pooja item if we loaded from bill
    if (poojaItemsToAdd.length > 0 || retailItemsToAdd.length > 0) {
        const firstPooja = document.getElementById('pooja_item_0');
        if (firstPooja && poojaCounter > poojaItemsToAdd.length) {
            firstPooja.remove();
            poojaCounter--;
            document.getElementById('poojaCount').value = poojaCounter;
        }
    }
}

getToday = () => {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
};


document.getElementById('billForm').addEventListener('submit', function (event) {
    
        const formData = new FormData(this);

        console.log('=== Form Data ===');

        for (const [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
        }

    const devoteeName = document.getElementById('devotee_name').value || '';
    const devoteeId = document.getElementById('devotee_id').value || '';
    const phoneEl = document.getElementById('new_devotee_phone');
    const phone = phoneEl ? (phoneEl.value || '').trim() : '';
    if (devoteeId == 0 && !phone) {
        event.preventDefault();
        alert('Please enter phone number for new devotee.');
    }

    const invalidFields = this.querySelectorAll(':invalid');

    if (invalidFields.length > 0) {

        console.log('Invalid fields:');

        invalidFields.forEach(field => {
            console.log({
                name: field.name,
                id: field.id,
                value: field.value,
                validationMessage: field.validationMessage
            });

            // Optional visual highlight
            field.style.border = '2px solid red';
        });

        // Focus first invalid field
        invalidFields[0].focus();

        // Prevent submit temporarily for debugging
        e.preventDefault();


        // -----------------------------
        // Log Submitted Data
        // -----------------------------
        const formData = new FormData(form);

        console.log('=== Form Data ===');

        for (const [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
        }
    }
});

// If user returns via browser back/forward, force fresh load to avoid stale bill data.
window.addEventListener('pageshow', function (event) {
    const navEntry = performance.getEntriesByType && performance.getEntriesByType('navigation')
        ? performance.getEntriesByType('navigation')[0]
        : null;
    const backForward = event.persisted || (navEntry && navEntry.type === 'back_forward');
    if (backForward) {
        window.location.replace('{{ url_for("billing.new_bill") }}');
    }
});


// Font Size Control System
class FontSizeManager {
    constructor() {
        this.minSize = 100;
        this.maxSize = 150;
        this.defaultSize = 100;
        this.step = 10;
        this.storageKey = 'billPageFontSize';

        this.init();
    }

    init() {
        // Load saved font size or use default
        const savedSize = parseInt(localStorage.getItem(this.storageKey)) || this.defaultSize;
        this.setFontSize(savedSize);

        // Attach event listeners
        document.getElementById('decreaseFontBtn').addEventListener('click', () => this.decreaseFont());
        document.getElementById('increaseFontBtn').addEventListener('click', () => this.increaseFont());
        document.getElementById('resetFontBtn').addEventListener('click', () => this.resetFont());
    }

    setFontSize(size) {
        // Clamp size between min and max
        size = Math.max(this.minSize, Math.min(this.maxSize, size));

        // Apply to entire form
        document.getElementById('billForm').style.fontSize = (size / 100) + 'em';

        // Also apply to font size display
        document.getElementById('fontSizeDisplay').textContent = size + '%';

        // Save to localStorage
        localStorage.setItem(this.storageKey, size);

        // Update button states
        this.updateButtonStates(size);
    }

    increaseFont() {
        const currentSize = parseInt(localStorage.getItem(this.storageKey)) || this.defaultSize;
        this.setFontSize(currentSize + this.step);
    }

    decreaseFont() {
        const currentSize = parseInt(localStorage.getItem(this.storageKey)) || this.defaultSize;
        this.setFontSize(currentSize - this.step);
    }

    resetFont() {
        this.setFontSize(this.defaultSize);
    }

    updateButtonStates(size) {
        const decreaseBtn = document.getElementById('decreaseFontBtn');
        const increaseBtn = document.getElementById('increaseFontBtn');

        // Disable decrease button if at minimum
        decreaseBtn.disabled = size <= this.minSize;

        // Disable increase button if at maximum
        increaseBtn.disabled = size >= this.maxSize;
    }
}

// Initialize font size manager when DOM is ready
let fontManager = null;