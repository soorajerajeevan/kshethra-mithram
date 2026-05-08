// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

// Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css';

// Import AG Grid
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';
import * as agGrid from 'ag-grid-community';

// Import jQuery
import $ from 'jquery';

// Import Tom Select
import 'tom-select/dist/css/tom-select.bootstrap5.css';
import TomSelect from 'tom-select';

// Make jQuery, TomSelect, and AG Grid available globally if needed
window.$ = $;
window.jQuery = $;
window.TomSelect = TomSelect;
window.agGrid = agGrid;

// Initialize Tom Select on all select elements with tom-select class
document.addEventListener('DOMContentLoaded', function() {
  const selects = document.querySelectorAll('select.form-select');
  selects.forEach(select => {
    new TomSelect(select, {
      create: false,
      placeholder: select.getAttribute('placeholder') || 'Select an option'
    });
  });
});
