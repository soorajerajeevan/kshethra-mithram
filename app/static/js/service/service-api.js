export async function fetchServices(filters = {}) {

    let url = '/poojas/api/services';
    const params = new URLSearchParams();
    if (filters.category) {
        params.append('category', filters.category);
    }
    if (filters.search) {
        params.append('search', filters.search);
    }
    if (params.toString()) {
        url += '?' + params.toString();
    }
    const response = await fetch(url);
    return await response.json();
}