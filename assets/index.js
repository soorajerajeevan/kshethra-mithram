// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

// Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css';

// Import AG Grid
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';
import { AllCommunityModule } from 'ag-grid-community';
import { ModuleRegistry } from 'ag-grid-community';
import * as agGrid from 'ag-grid-community';
ModuleRegistry.registerModules([ AllCommunityModule ]);

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