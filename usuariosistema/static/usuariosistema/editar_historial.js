const tipo = document.getElementById('id_tipo');
const persona = document.getElementById('id_persona');
const personaField = document.getElementById('button-vincular');
const clearButton = document.getElementById('clear-button');
const vincularBtn = document.getElementById('vincular');
const usuarioList = document.getElementById('personas');
const searchBar = document.getElementById('buscar_socio');

let usuario = [];
let buttons = [];
let searchString = '';
let currentPage = 1;

tipo.addEventListener('change', (e) => {
  if (e.target.value == 'SOCIO') {
    vincularBtn.style.display = 'inline';
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
    persona.value = e.target.id;
    personaField.innerHTML = e.target.innerHTML;
  }
});

const loadUsuarios = async () => {
  try {
    const res = await fetch(`/usuario/fetch?filter-string=${searchString.toLowerCase()}&page=${currentPage}`)
    usuarios = await res.json();
    buttons = usuarios[usuarios.length - 1]
    usuarios.pop(usuarios.length - 1)
    drawRows();
  } catch (err) {
    console.error(err);
  }
};

const drawRows = () => {
  const returnString = usuarios.map((usuario) => {
    return `
      <tr class="socio">
        <td id="${usuario.id}" onMouseOver="this.style.color='blue'; this.style.cursor='pointer'" onMouseOut="this.style.color='black'" data-dismiss="modal">${usuario.nombre_apellido}</td>
      </tr>
    `;
  }).join('');
  usuarioList.innerHTML = returnString;
};
