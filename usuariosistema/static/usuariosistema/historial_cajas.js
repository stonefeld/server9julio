const masInfoBtn = document.getElementsByClassName('mas-info-btn');
const modal = document.getElementById('ciclos-caja');
const total = document.getElementById('total-recaudado');

var cajas = [];
var recaudado = 0;
var mes = 0;
var orderBy = 'cicloCaja';

document.getElementById('cicloCaja').addEventListener('click', () => {
  if (orderBy !== 'cicloCaja') {
    orderBy = 'cicloCaja';
  } else {
    orderBy = '-cicloCaja';
  }
  loadCiclosCaja();
});

document.getElementById('inicioCaja').addEventListener('click', () => {
  if (orderBy !== 'inicioCaja') {
    orderBy = 'inicioCaja';
  } else {
    orderBy = '-inicioCaja';
  }
  loadCiclosCaja();
});

document.getElementById('finalCaja').addEventListener('click', () => {
  if (orderBy !== 'finalCaja') {
    orderBy = 'finalCaja';
  } else {
    orderBy = '-finalCaja';
  }
  loadCiclosCaja();
});

document.getElementById('recaudado').addEventListener('click', () => {
  if (orderBy !== 'recaudado') {
    orderBy = 'recaudado';
  } else {
    orderBy = '-recaudado';
  }
  loadCiclosCaja();
});

document.getElementById('usuarioCaja').addEventListener('click', () => {
  if (orderBy !== 'usuarioCaja') {
    orderBy = 'usuarioCaja';
  } else {
    orderBy = '-usuarioCaja';
  }
  loadCiclosCaja();
});

const loadCiclosCaja = async () => {
  try {
    const res = await fetch(`/menu_estacionamiento/cicloscaja/fetch?mes=${mes}&order-by=${orderBy}`);
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
      mes = e.target.id;
      loadCiclosCaja();
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
