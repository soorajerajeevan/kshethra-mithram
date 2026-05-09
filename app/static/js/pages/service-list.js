
import { ServiceColumnDefs } from '../ag-grid/service-list-columns.js';
import { fetchServices } from '../service/service-api.js';


let gridApi;
let gridColumnApi;
let modifiedRows = new Set();
let poojaServices = [];

// Initialize grid when DOM is ready
document.addEventListener('DOMContentLoaded', initializeGrid);

// Initialize AG Grid
function initializeGrid() {
    const eGridDiv = document.querySelector('#serviceGrid');
    const gridOptions = {
        columnDefs: ServiceColumnDefs,
        rowData: [],
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true
        },
        rowSelection: 'multiple',
        theme: "legacy",
        suppressRowClickSelection: false,
        onCellValueChanged: function (params) {
            if (params.data.id) {
                modifiedRows.add(params.data.id);
                document.getElementById('updateChangesBtn').disabled = modifiedRows.size === 0;
            }
        },
        onRowDataUpdated: function () {
            if (modifiedRows.size > 0) {
                document.getElementById('updateChangesBtn').disabled = false;
            }
        }
    };
    
    gridApi = agGrid.createGrid(eGridDiv, gridOptions);
    
    // Load initial data
    loadServices();

}


// Update Changes button
document.getElementById('updateChangesBtn').addEventListener('click', function () {
    const allRows = [];
    gridApi.forEachNode(node => {
        allRows.push(node.data);
    });

    const updateData = {
        services: allRows,
        modified_ids: Array.from(modifiedRows)
    };
    
    fetch('/poojas/services/update-batch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Changes saved successfully!');
                modifiedRows.clear();
                document.getElementById('updateChangesBtn').disabled = true;
                location.reload();
            } else {
                alert('Error: ' + (data.message || 'Failed to save changes'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error saving changes: ' + error);
        });
});

async function loadServices() {
    try {
        const services = await fetchServices();
        gridApi.setGridOption('rowData', services);
    } catch (error) {
        console.error('Error loading services:', error);
    }
}