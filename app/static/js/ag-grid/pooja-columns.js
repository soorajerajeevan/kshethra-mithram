import { currencyFormatter } from './formatters.js';
import { billSpanMatcher } from './grid-utils.js';

    export const poojaColumnDefs = [
                {
                    headerName: 'Bill Number',
                    field: 'billNumber',
                    width: 145,
                    minWidth: 145,
                    spanRows: billSpanMatcher,
                    filter: true,
                    sortable: true
                },
                {
                    headerName: 'User',
                    field: 'devoteeName',
                    width: 140,
                    spanRows: billSpanMatcher,
                    filter: true,
                    sortable: true
                },
                {
                    headerName: 'Bill Date',
                    field: 'billDate',
                    spanRows: billSpanMatcher,
                    width: 130,
                    filter: true,
                    sortable: true,
                    cellClass: 'right-border-column'
                },
                {
                    headerName: 'Devotee',
                    field: 'memberName',
                    width: 140,
                    minWidth: 130
                },
                {
                    headerName: 'Nakshathram',
                    field: 'memberNakshathram',
                    width: 160,
                    minWidth: 130
                },
                {
                    headerName: 'Pooja',
                    field: 'poojaName',
                    width: 180,
                    minWidth: 130
                },
                {
                    headerName: 'Notes',
                    field: 'notes',
                    width: 180,
                    minWidth: 130
                },
                {
                    headerName: 'Scheduled',
                    field: 'billDate',
                    width: 140
                },
                {
                    headerName: 'QTY',
                    field: 'quantity',
                    width: 50,
                    type: 'numericColumn'
                },
                {
                    headerName: 'Price',
                    field: 'unitPrice',
                    width: 100,
                    type: 'numericColumn',
                    valueFormatter: params => params.value ? '₹' + params.value.toLocaleString('en-IN') : ''
                },
                {
                    headerName: 'Total',
                    field: 'totalPrice',
                    width: 120,
                    type: 'numericColumn',
                    valueFormatter: params => params.value ? '₹' + params.value.toLocaleString('en-IN') : ''
                },
                {
                    headerName: 'Sub Total',
                    field: 'subtotal',
                    width: 120,
                    type: 'numericColumn',
                    valueFormatter: params => params.value ? '₹' + params.value.toLocaleString('en-IN') : '',
                    spanRows: billSpanMatcher,
                    cellClass: 'left-border-column'
                },
                {
                    headerName: 'Discount',
                    field: 'discountAmount',
                    width: 120,
                    type: 'numericColumn',
                    valueFormatter: params => params.value ? '₹' + params.value.toLocaleString('en-IN') : '',
                    spanRows: billSpanMatcher
                },
                {
                    headerName: 'Donation',
                    field: 'donationAmount',
                    width: 120,
                    type: 'numericColumn',
                    valueFormatter: params => params.value ? '₹' + params.value.toLocaleString('en-IN') : '',
                    spanRows: billSpanMatcher
                },
                {
                    headerName: 'Grant Total',
                    field: 'grandTotal',
                    width: 140,
                    type: 'numericColumn',
                    valueFormatter: params => params.value ? '₹' + params.value.toLocaleString('en-IN') : '',
                    spanRows: billSpanMatcher
                },
                {
                    headerName: 'Payment Mode',
                    field: 'paymentMode',
                    width: 130,
                    spanRows: billSpanMatcher,
                    filter: true,
                    sortable: true
                },
                {
                    headerName: 'Reference',
                    field: 'paymentReference',
                    width: 150,
                    spanRows: billSpanMatcher
                },
                {
                    headerName: 'Notes',
                    field: 'notes',
                    width: 200,
                    tooltipField: 'notes',
                    spanRows: billSpanMatcher
                }
            ];  