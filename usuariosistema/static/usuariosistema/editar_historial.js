const tipoGeneral = document.getElementById('tipo-general');
const tipo = document.getElementById('id_tipo');

const persona = document.getElementById('id_persona');
const proveedor = document.getElementById('id_proveedor');

const usuarioList = document.getElementById('personas');
const searchBar = document.getElementById('buscar_socio');
const clearButton = document.getElementById('clear-button');

const personaField = document.getElementById('button-vincular');
const formPersona = document.getElementById('form-persona');
const vincularBtn = document.getElementById('vincular');

let usuario = [];
let buttons = [];
let searchString = '';
let currentPage = 1;

tipo.addEventListener('change', (e) => {
  if (e.target.value == 'SOCIO' || e.target.value == 'SOCIO-MOROSO') {
    if (tipoGeneral.innerHTML != 'socio') {
      vincularBtn.style.display = 'inline';
    }   
  } else {
    vincularBtn.style.display = 'none';
  }
});

clearButton.addEventListener('click', () => {
  searchBar.value = '';
  searchString = '';
  currentPage = 1;
  usuarios = [];
  drawRows();
});

searchBar.addEventListener('keyup', (e) => {
  searchString = e.target.value.toLowerCase();
  currentPage = 1;
  loadUsuarios();
});

document.querySelector('body').addEventListener('click', (e) => {
  if (e.target.tagName.toLowerCase() === 'td') {
    if (tipoGeneral.innerHTML == 'socio' || tipoGeneral.innerHTML == 'nosocio') {
      persona.value = e.target.id;
    } else if (tipoGeneral.innerHTML == 'proveedor') {
      proveedor.value = e.target.id;
    }
    personaField.innerHTML = e.target.innerHTML;
    formPersona.style.display = 'inline';
    vincularBtn.style.display = 'none';
  }
});

const loadUsuarios = async () => {
  try {
    if (tipoGeneral.innerHTML == 'socio' || tipoGeneral.innerHTML == 'nosocio') {
      const res = await fetch(`/usuario/fetch?filter-string=${searchString.toLowerCase()}&page=${currentPage}`)
      usuarios = await res.json();
    } else if (tipoGeneral.innerHTML == 'proveedor') {
      const res = await fetch(`/estacionamiento/fetch?filter-string=${searchString.toLowerCase()}&page=${currentPage}`)
      usuarios = await res.json();
    }
    buttons = usuarios[usuarios.length - 1]
    usuarios.pop(usuarios.length - 1)
    drawRows();
  } catch (err) {
    console.error(err);
  }
};

const drawRows = () => {
  const returnString = usuarios.map((usuario) => {
    if (tipoGeneral.innerHTML == 'socio' || tipoGeneral.innerHTML == 'nosocio') {
      return `
        <tr class="socio">
          <td id="${usuario.id}" onMouseOver="this.style.color='blue'; this.style.cursor='pointer'" onMouseOut="this.style.color='black'" data-dismiss="modal">${usuario.nombre_apellido}</td>
        </tr>
      `;
    } else if (tipoGeneral.innerHTML == 'proveedor') {
      return `
        <tr class="socio">
          <td id="${usuario.id}" onMouseOver="this.style.color='blue'; this.style.cursor='pointer'" onMouseOut="this.style.color='black'" data-dismiss="modal">${usuario.nombre_proveedor}</td>
        </tr>
      `;
    }
  }).join('');
  usuarioList.innerHTML = returnString;
};
