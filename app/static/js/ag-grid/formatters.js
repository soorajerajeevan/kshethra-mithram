export function currencyFormatter(params) {
    return params.value
        ? '₹' + Number(params.value).toLocaleString('en-IN')
        : '';
}