export async function fetchPoojaList(filters = {}) {

    let url = '/billing/api/pooja-list';
    const params = new URLSearchParams();

    if (filters.startDate) {
        params.append('startDate', filters.startDate);
    }
    if (filters.endDate) {
        params.append('endDate', filters.endDate);
    }
    if (filters.poojaServiceId) {
        params.append('poojaServiceId', filters.poojaServiceId);
    }
    if (params.toString()) {
        url += '?' + params.toString();
    }
    const response = await fetch(url);
    return await response.json();
}
