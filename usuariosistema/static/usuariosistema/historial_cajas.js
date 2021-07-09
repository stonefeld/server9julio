const masInfoBtn = document.getElementsByClassName('mas-info-btn');
const modal = document.getElementById('ciclos-caja');
const total = document.getElementById('total-recaudado');

var cajas = [];
var recaudado = 0;

const loadCiclosCaja = async (mes) => {
  try {
    const res = await fetch(`/menu_estacionamiento/cicloscaja/fetch?mes=${mes}`);
    cajas = await res.json();
    drawCiclosCaja();
  } catch (err) {
    console.error(err);
  }
}

document.querySelector('body').addEventListener('click', (e) => {
  if (e.target.tagName.toLowerCase() === 'button') {
    if (e.target.innerHTML === '+') {
      recaudado = document.getElementById(`recaudado-${e.target.id}`).innerHTML;
      loadCiclosCaja(e.target.id);
    }
  }
});

const drawCiclosCaja = () => {
  const returnString = cajas.map((caja) => {
    const inicioFecha = new Date(caja.inicioCaja).toLocaleString('es-AR', {
      timeZone: 'America/Argentina/Buenos_Aires'
    });
    var finalFecha;
    if (caja.finalCaja === null) {
      finalFecha = 'No cerró';
    } else {
      finalFecha = new Date(caja.finalCaja).toLocaleString('es-AR', {
        timeZone: 'America/Argentina/Buenos_Aires'
      });
    }
    if (caja.recaudado === null) {
      caja.recaudado = 'No cerró';
    } else {
      caja.recaudado = `$${caja.recaudado}`;
    }
    if (caja.user === null) caja.user = 'No cerró';
    return `
      <tr class="ciclo-caja">
        <td>${caja.cicloCaja}</td>
        <td>${inicioFecha}</td>
        <td>${finalFecha}</td>
        <td>${caja.recaudado}</td>
        <td>${caja.user}</td>
      </tr>
    `;
  }).join('');
  total.innerHTML = `Total recaudado: ${recaudado}`;
  modal.innerHTML = returnString;
}

const drawButtons = () => {
  for (var i = 0; i < masInfoBtn.length; i++) {
    masInfoBtn[i].innerHTML = `
      <button id='${masInfoBtn[i].id}' class="btn btn-outline-info" data-toggle="modal" data-target="#exampleModal">+</button>
    `;
  }
}

drawButtons();
