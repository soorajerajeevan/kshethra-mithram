export function billSpanMatcher(params) {

    const rowA = params.nodeA?.data || null;
    const rowB = params.nodeB?.data || null;

    if (!rowA || !rowB) {
        return false;
    }

    if (!rowA.billNumber || !rowB.billNumber) {
        return false;
    }

    return rowA.billNumber === rowB.billNumber;
}