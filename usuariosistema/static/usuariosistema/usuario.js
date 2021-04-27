const searchBar = document.getElementById('buscar');
const clearButton = document.getElementById('clear-button');
const usuarioList = document.getElementById('usuarios');
const navButtons = document.getElementById('navbuttons');

let usuario = [];
let buttons = [];
let searchString = '';
let currentPage = 1;

clearButton.addEventListener('click', () => {
  searchBar.value = '';
  searchString = '';
  currentPage = 1;
  loadUsuarios();
});

searchBar.addEventListener('keyup', (e) => {
  searchString = e.target.value.toLowerCase();
  currentPage = 1;
  loadUsuarios();
});

const loadUsuarios = async () => {
  try {
    const res = await fetch(`/usuario/fetch?filter-string=${searchString.toLowerCase()}&page=${currentPage}`)
    usuarios = await res.json();
    buttons = usuarios[usuarios.length - 1]
    usuarios.pop(usuarios.length - 1)
    drawRows();
    drawButtons();
  } catch (err) {
    console.error(err);
  }
};

const drawRows = () => {
  const returnString = usuarios.map((usuario) => {
    return `
      <tr class="usuario">
        <td>${usuario.nrSocio}</td>
        <td><a href="${usuario.id}">${usuario.nombre_apellido}</a></td>
      </tr>
    `;
  }).join('');
  usuarioList.innerHTML = returnString;
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
  loadUsuarios(currentPage++);
};

const prevPage = () => {
  loadUsuarios(currentPage--);
};

loadUsuarios();
