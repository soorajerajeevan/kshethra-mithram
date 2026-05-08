// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

// Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css';

// Import jQuery
import $ from 'jquery';

// Import Tom Select
import 'tom-select/dist/css/tom-select.bootstrap5.css';
import TomSelect from 'tom-select';

// Make jQuery and TomSelect available globally if needed
window.$ = $;
window.jQuery = $;
window.TomSelect = TomSelect;

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
