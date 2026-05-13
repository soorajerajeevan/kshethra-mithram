import { currencyFormatter } from './formatters.js';
import { billSpanMatcher } from './grid-utils.js';


export const ServiceColumnDefs = [
    {
        headerName: 'Number',
        field: 'id',
        editable: false,
        flex: 0.5,
        minWidth: 100,
        cellDataType: 'number'
    },
    {
        headerName: 'Malayalam Name',
        field: 'malayalam_name',
        editable: true,
        flex: 1,
        minWidth: 150,
        cellDataType: 'text'
    },
    {
        headerName: 'English Name',
        field: 'english_name',
        editable: true,
        flex: 1,
        minWidth: 150,
        cellDataType: 'text'
    },
    {
        headerName: 'Category',
        field: 'category',
        editable: true,
        flex: 1,
        minWidth: 120,
        cellDataType: 'text'
    },
    {
        headerName: 'Price (₹)',
        field: 'default_price',
        editable: true,
        flex: 0.8,
        minWidth: 100,
        cellDataType: 'number',
        valueFormatter: currencyFormatter
    },
    {
        headerName: 'Max Bookings/Day',
        field: 'max_bookings_per_day',
        editable: true,
        flex: 0.9,
        minWidth: 100,
        cellDataType: 'number'
    },
    {
        headerName: 'Show in Booking',
        field: 'add_to_booking',
        cellRenderer: 'agCheckboxCellRenderer',
        cellEditor: 'agCheckboxCellEditor',
        editable: true,
        flex: 0.8,
        minWidth: 100
    },
    {
        headerName: 'Active',
        field: 'is_active',
        cellRenderer: 'agCheckboxCellRenderer',
        cellEditor: 'agCheckboxCellEditor',
        editable: true,
        flex: 0.6,
        minWidth: 80
    },
    {
        headerName: 'Actions',
        field: 'id',
        width: 150,
        sortable: false,
        filter: false,
        cellRenderer: function(params) {
            const div = document.createElement('div');
            div.className = 'action-buttons';
            
            const editBtn = document.createElement('a');
            editBtn.href = '{{ url_for("poojas.services_edit", id="1") }}'.replace('__ID__', params.value);
            editBtn.className = 'btn btn-sm btn-warning';
            editBtn.innerHTML = '<i class="bi bi-pencil"></i> Edit';
            
            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'btn btn-sm btn-danger';
            deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Delete';
            deleteBtn.onclick = function(e) {
                e.preventDefault();
                if (confirm('Are you sure you want to delete this row?')) {
                    gridApi.applyTransaction({ remove: [params.data] });
                }
            };
            
            div.appendChild(editBtn);
            // div.appendChild(deleteBtn);
            return div;
        }
    }
];