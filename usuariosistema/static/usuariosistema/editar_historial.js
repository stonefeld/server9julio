// DISCLAIMER: la mayoria de las variables se tienen nombre relacionado con usuario/socio/persona,
// pero interactua muchas veces con los proveedores. El tema es que inicialmente lo habia hecho
// para socios y cuando agregue la misma funcionalidad pero para proveedores, no cambie el nombre
// de las variables para evitar la mayor cantidad de problemas. Van a notar que hay ifs preguntando
// si el tipo es socio o proveedor y aun asi interactuo con las variables que tienen por nombre algo
// relacionado a los socios o personas. Por tu bien y el del codigo, no cambiarlo!!!.

const tipoGeneral = document.getElementById('tipo-general'); // Para saber cual era el tipo original de la entrada.
const tipo = document.getElementById('id_tipo'); // Para saber el tipo seleccionado en el form.

const persona = document.getElementById('id_persona'); // El input tag de la persona (esta oculto por default).
const proveedor = document.getElementById('id_proveedor'); // Idem anterior pero del proveedor (esta oculto por default).

const usuarioList = document.getElementById('personas'); // La tabla donde se van a renderizar los usuarios o proveedores filtrados.
const searchBar = document.getElementById('buscar_socio'); // El tag de la barra de busqueda.
const clearButton = document.getElementById('clear-button'); // El boton para borrar la busqueda.

const personaField = document.getElementById('button-vincular'); // El boton que se presiona para activar el modal donde se hace la busqueda correspondiente.
const formPersona = document.getElementById('form-persona'); // El div oculto por default para hacer aparecer cuando se pasa de NOSOCIO a SOCIO/SOCIO-MOROSO.
const vincularBtn = document.getElementById('vincular'); // El boton para vincular al socio.

let usuario = [];
let buttons = [];
let searchString = '';
let currentPage = 1;

// Este EventListener detecta cuando se realiza un cambio en el tag de tipo.
tipo.addEventListener('change', (e) => {
  // Chequea si es socio.
  if (e.target.value == 'SOCIO' || e.target.value == 'SOCIO-MOROSO') {
    // Verifica que la entrada no sea originalmente de un socio (no tiene sentido hacer aparecer el boton
    // de vincular socio si ya esta el campo de button-vincular visible).
    if (tipoGeneral.innerHTML != 'socio') {
      vincularBtn.style.display = 'inline';
    }
  } else {
    // Si no se selecciono el tipo socio o se cambio a uno distinto hacer desaparecer el boton.
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

// Esta funcion chequea que una vez que se hizo el fetch de los proveedores o socios en el modal
// si se toca algun campo. Como estos campos se renderizan dinamicamente en este js, necesito
// activar un EventListener que funcione con estos campos. Entonces chqueo si se hizo click
// en alguna parte del doucmento y si el tag sobre el que se hizo click es un <td> que es el
// campo de cada row en la tabla del modal.
document.querySelector('body').addEventListener('click', (e) => {
  if (e.target.tagName.toLowerCase() === 'td') {
    // Si es socio o nosocio quiero que asigne el valor al form de persona, sino al form de
    // proveedor.
    if (tipoGeneral.innerHTML == 'socio' || tipoGeneral.innerHTML == 'nosocio') {
      persona.value = e.target.id;
    } else if (tipoGeneral.innerHTML == 'proveedor') {
      proveedor.value = e.target.id;
    }
    // Hago visible el boton que muestra el socio/proveedor seleccionado y que al clickear
    // abre el modal para seleccionar otro socio/proveedor.
    personaField.innerHTML = e.target.innerHTML;
    formPersona.style.display = 'inline';
    // Hago desaparecer el boton de 'Vincular socio', ya que ya esta visible el boton
    // que si hago click sobre el cumple la misma funcion.
    vincularBtn.style.display = 'none';
  }
});

const loadUsuarios = async () => {
  try {
    // Si es socio/socio-moroso quiero hacer el fetch a la url que me devuelve la lista
    // filtrada de socios, sino que lo haga a la lista de proveedores.
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
    // Aca hay que chequear el tipo nuevamente, ya que si es socio los campos del model
    // son distintos a los del proveedor, sino me renderiza el nombre 'undefined' ya que
    // los campos se llaman distinto.
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
