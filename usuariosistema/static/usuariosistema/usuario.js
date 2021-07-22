const searchBar = document.getElementById('buscar');
const clearButton = document.getElementById('clear-button');
const usuarioList = document.getElementById('usuarios');
const navButtons = document.getElementById('navbuttons');

let usuario = [];
let buttons = [];
let searchString = '';
let currentPage = 1;
let orderBy = 'nombre_apellido';

document.getElementById('nrSocio').addEventListener('click', () => {
  if (orderBy !== 'nrSocio') {
    orderBy = 'nrSocio';
  } else {
    orderBy = '-nrSocio';
  }
  loadUsuarios();
});

document.getElementById('nombre_apellido').addEventListener('click', () => {
  if (orderBy !== 'nombre_apellido') {
    orderBy = 'nombre_apellido';
  } else {
    orderBy = '-nombre_apellido';
  }
  loadUsuarios();
});

document.getElementById('nrTarjeta').addEventListener('click', () => {
  if (orderBy !== 'nrTarjeta') {
    orderBy = 'nrTarjeta';
  } else {
    orderBy = '-nrTarjeta';
  }
  loadUsuarios();
});

document.getElementById('dni').addEventListener('click', () => {
  if (orderBy !== 'dni') {
    orderBy = 'dni';
  } else {
    orderBy = '-dni';
  }
  loadUsuarios();
});

document.getElementById('general').addEventListener('click', () => {
  if (orderBy !== 'general') {
    orderBy = 'general';
  } else {
    orderBy = '-general';
  }
  loadUsuarios();
});

document.getElementById('estacionamiento').addEventListener('click', () => {
  if (orderBy !== 'estacionamiento') {
    orderBy = 'estacionamiento';
  } else {
    orderBy = '-estacionamiento';
  }
  loadUsuarios();
});

document.getElementById('deuda').addEventListener('click', () => {
  if (orderBy !== 'deuda') {
    orderBy = 'deuda';
  } else {
    orderBy = '-deuda';
  }
  loadUsuarios();
});

clearButton.addEventListener('click', () => {
  searchBar.value = '';
  searchString = '';
  currentPage = 1;
  orderBy = 'nombre_apellido';
  loadUsuarios();
});

searchBar.addEventListener('keyup', (e) => {
  searchString = e.target.value.toLowerCase();
  currentPage = 1;
  loadUsuarios();
});

const loadUsuarios = async () => {
  try {
    const res = await fetch(`/usuario/fetch?filter-string=${searchString.toLowerCase()}&page=${currentPage}&order-by=${orderBy}`)
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
    if (usuario.dni == null) { usuario.dni = 'No establecido'; }
    if (usuario.nrTarjeta == null) { usuario.nrTarjeta = 'No establecido'; }
    if (usuario.general) {
      usuario.general = 'SI';
    } else {
      usuario.general = 'NO';
    }
    if (usuario.estacionamiento) {
      usuario.estacionamiento = 'SI';
    } else {
      usuario.estacionamiento = 'NO';
    }
    return `
      <tr class="usuario">
        <td>${usuario.nrSocio}</td>
        <td><a href="/usuario/lista/${usuario.id}">${usuario.nombre_apellido}</a></td>
        <td>${usuario.nrTarjeta}</td>
        <td>${usuario.dni}</td>
        <td>${usuario.general}</td>
        <td>${usuario.estacionamiento}</td>
        <td>$ ${usuario.deuda}</td>
      </tr>
    `;
  }).join('');
  usuarioList.innerHTML = returnString;
};

const drawButtons = () => {
  if (buttons.has_previous && buttons.has_next) {
    navButtons.innerHTML = `
      <li class="previous page-item"><a href="javascript:prevPage()" class="page-link">Anterior</a></li>
      <li class="next page-item"><a href="javascript:nextPage()" class="page-link">Siguiente</a></li>
    `;
  } else if (buttons.has_previous && ~buttons.has_next) {
    navButtons.innerHTML = `
      <li class="page-item"><a href="javascript:prevPage()" class="page-link">Anterior</a></li>
    `;
  } else if (~buttons.has_previous && buttons.has_next) {
    navButtons.innerHTML = `
      <li class="page-item"><a href="javascript:nextPage()" id="btn-prev" class="page-link">Siguiente</a></li>
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
