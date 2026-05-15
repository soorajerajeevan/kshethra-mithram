
import { poojaColumnDefs } from '../ag-grid/pooja-columns.js';

let gridApi, columnApi;
let poojaServices = [];


// Initialize grid when DOM is ready
document.addEventListener('DOMContentLoaded', initializeGrid);


// Apply filters
window.applyFilters = function () {
    loadPoojaData();
}

// Reset filters
window.resetFilters = function () {
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    document.getElementById('filterPooja').value = '';
    loadPoojaData();
}
window.exportPoojaGrid = function () {

    gridApi.exportDataAsCsv({
        fileName: 'pooja-list.csv'
    });
};


// Initialize AG Grid
function initializeGrid() {
    const gridDiv = document.getElementById('poojaGrid');

    const gridOptions = {
        columnDefs: poojaColumnDefs,
        rowData: [],
        defaultColDef: {
            flex: 1,
            resizable: true,
            sortable: false,
            cellStyle: { display: 'flex', 'align-items': 'center' },
            filter: false
        },
        enableCellSpan: true,
        domLayout: 'normal',
        theme: "legacy",
        pagination: false
    };

    gridApi = agGrid.createGrid(gridDiv, gridOptions);

    // Load initial data
    loadPoojaData();
    loadPoojaServices();

}

// Load pooja services for filter dropdown
function loadPoojaServices() {
    fetch('/poojas/api/list')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filterPooja');
            data = data.sort((a, b) => a.id - b.id);
            const el = document.querySelector('#filterPooja');
            if (!el || typeof TomSelect === 'undefined') return null;
            if (el.tomselect) return el.tomselect;
            new TomSelect(el, {
                maxItems: null,
                valueField: 'id',
                labelField: 'display_name',
                searchField: ['english_name', 'id', 'malayalam_name'],
                options: data,
                create: false
            });

        })
        .catch(error => console.error('Error loading pooja services:', error));
}

function poojaLabel(p) { return `${p.id} - ${p.malayalam_name} || ${p.english_name}`; }

// Load pooja data from API
function loadPoojaData() {
    const startDate = document.getElementById('filterStartDate').value;
    const endDate = document.getElementById('filterEndDate').value;
    const poojaId = document.getElementById('filterPooja').value;

    let url = '/billing/api/pooja-list';
    const params = new URLSearchParams();

    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);
    if (poojaId) params.append('poojaServiceId', poojaId);

    if (params.toString()) {
        url += '?' + params.toString();
    }
    let gridData = [];
    fetch(url)
        .then(response => response.json())
        .then(bills => {

            let gridData = [];
            console.log('Loaded Pooja Data:', bills);
            for (const bill of bills) {
                bill.billDate = new Date(bill.billDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
                bill.items.forEach(item => {
                    gridData.push({
                        billNumber: bill.billNumber,
                        devoteeName: bill.devoteeName,
                        memberNakshathram: item.memberNakshathram,
                        memberName: item.memberName,
                        billDate: bill.billDate,
                        poojaName: item.service.name,
                        quantity: item.quantity,
                        unitPrice: item.unitPrice,
                        totalPrice: item.totalPrice,
                        subtotal: bill.subtotal,
                        discountAmount: bill.discountAmount,
                        donationAmount: bill.donationAmount,
                        grandTotal: bill.grandTotal,
                        paymentMode: bill.paymentMode,
                        paymentReference: bill.paymentReference,
                        notes: item.notes,
                        rowSpan: bill.items.length
                    });
                });
            }
            gridApi.setGridOption('rowData', gridData);

            gridApi.redrawRows();
        })
        .catch(error => console.error('Error loading pooja data:', error));
}


function billSpanMatcher(params) {
    const rowA = params.nodeA?.data ? params.nodeA.data : null;
    const rowB = params.nodeB?.data ? params.nodeB.data : null;

    // Safety checks
    if (!rowA || !rowB) {
        return false;
    }

    // Prevent spanning empty bill IDs
    if (!rowA.billNumber || !rowB.billNumber) {
        return false;
    }
    // Merge only same bill
    return rowA.billNumber === rowB.billNumber;
}


function initSearchableSelect(selector, options = {}) {
    const el = document.querySelector(selector);
    if (!el || typeof TomSelect === 'undefined') return null;
    if (el.tomselect) return el.tomselect;
    return new TomSelect(el, {
        maxOptions: 100,
        closeAfterSelect: true,
        ...options
    });
}
