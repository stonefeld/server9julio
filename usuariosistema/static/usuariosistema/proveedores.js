const searchBar = document.getElementById('buscar');
const clearButton = document.getElementById('clear-button');
const proveedoresList = document.getElementById('proveedores');
const navButtons = document.getElementById('navbuttons');

let proveedores = [];
let buttons = [];
let searchString = '';
let currentPage = 1;

clearButton.addEventListener('click', () => {
  searchBar.value = '';
  searchString = '';
  currentPage = 1;
  loadProveedores();
});

searchBar.addEventListener('keyup', (e) => {
  searchString = e.target.value.toLowerCase();
  currentPage = 1;
  loadProveedores();
  drawRows(proveedores);
});

const loadProveedores = async () => {
  try {
    const res = await fetch(`/estacionamiento/proveedor/fetch?filter-string=${searchString.toLowerCase()}&page=${currentPage}`)
    proveedores = await res.json();
    buttons = proveedores[proveedores.length - 1]
    proveedores.pop(proveedores.length - 1)
    drawRows();
    drawButtons();
  } catch (err) {
    console.error(err);
  }
};

const drawRows = () => {
  const returnString = proveedores.map((proveedor) => {
    return `
      <tr class="proveedor">
        <td>${proveedor.idProveedor}</td>
        <td><a href="/estacionamiento/proveedor/${proveedor.id}/" style="text-decoration:none">${proveedor.nombre_proveedor}</a></td>
      </tr>
    `;
  }).join('');
  proveedoresList.innerHTML = returnString;
};

const drawButtons = () => {
  if (buttons.has_previous && buttons.has_next) {
    navButtons.innerHTML = `
        <a href="javascript:prevPage()" class="btn btn-outline-info mb-4">Anterior</a>
        <a href="javascript:nextPage()" class="btn btn-outline-info mb-4">Siguiente</a>
    `;
  } else if (buttons.has_previous && ~buttons.has_next) {
    navButtons.innerHTML = `
        <a href="javascript:prevPage()" class="btn btn-outline-info mb-4">Anterior</a>
    `;
  } else if (~buttons.has_previous && buttons.has_next) {
    navButtons.innerHTML = `
        <a href="javascript:nextPage()" id="btn-prev" class="btn btn-outline-info mb-4">Siguiente</a>
    `;
  } else {
    navButtons.innerHTML = ``;
  }
};

const nextPage = () => {
  loadProveedores(currentPage++);
};

const prevPage = () => {
  loadProveedores(currentPage--);
};

loadProveedores();
