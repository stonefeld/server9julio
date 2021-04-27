let nav = 0;
let clicked = null;
let events = localStorage.getItem('events') ? JSON.parse(localStorage.getItem('events')) : [];
//a tener en cuenta que lo que dice "Padding" hace referencia a los dias que siempre sobran en el calendario del mes anterior
// const calendar = document.getElementById('calendar');
const calendar = document.querySelector('#calendar');
const newTarifaModal = document.getElementById('newTarifaModal');
const deleteTarifaModal = document.getElementById('deleteTarifaModal');
const backDrop = document.getElementById('modalBackDrop');
const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];



function openModal(date){
  clicked = date
  const tarifaEspecialForDay = events.find
  (e => e.date === clicked);

  if(tarifaEspecialForDay){
    document.getElementById('fechaTarifaEspecial').innerText = tarifaEspecialForDay.date
    deleteTarifaModal.style.display = 'block'
  }else{
    newTarifaModal.style.display = 'block';
  }

  backDrop.style.display = 'block';
}

const loadEvents = async () => {
  try {
    const res = await fetch(`/estacionamiento/fetch_Events`);
    events = await res.json();
    load();
  } catch (err) {
    console.error(err);
  }
};

const load = () => {
  //tener en cuenta que Date toma como 0 el mes de Enero como si fuera un array [Enero, Febrero, Marzo, etc]
  // Día de semana, Mes, Día Numero, Año, Hora
  

  const dt = new Date();

  if(nav !== 0){
    dt.setMonth(new Date().getMonth() + nav);
  }

  const day = dt.getDate();
  const month = dt.getMonth();
  const year = dt.getFullYear();

  const firstDayOfMonth= new Date(year, month, 1);

  /*
  el tercer num es el dia, y el primer dia del mes es 1, si le pasamos 0 es el ultimo dia del mes anterior
  y como le estamos pasando el mes siguiente nos va a dar los dias de el mes actual
  */
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  //dateString ejemplo de lo que devuelve jueves, 01/04/2021 (prestar atencion a la coma)
  const dateString = firstDayOfMonth.toLocaleDateString('en-us',{
    weekday: 'long',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',

  });
  const paddingDays = weekdays.indexOf(dateString.split(', ')[0]);

  document.getElementById('monthDisplay').innerText= 
  `${dt.toLocaleDateString('es-ar',{month: 'long'})} ${year}`

  //limpiamos el calendarios sino en cada load() va a crear otro calendario
  calendar.innerHTML = '';
  
  for(let i= 1; i <= paddingDays + daysInMonth; i++){
    const daySquare = document.createElement('div');
    daySquare.classList.add('day');

    const dayString=`${i-paddingDays}/${month+1}/${year}`

    if(i > paddingDays){
      daySquare.innerText = i - paddingDays;

      const tarifaEspecialForDay = events.find(e => e.date === dayString);

      if(i - paddingDays === day && nav === 0){
        daySquare.id = 'currentDay'
      }

      //aca creas un div con estilo tarifa (CSS) que dice "Tarifa Especial" para el dia que guardaste
      if(tarifaEspecialForDay){
        const avisoDiv = document.createElement('div')
        avisoDiv.classList.add('tarifa');
        avisoDiv.innerText='Tarifa especial'
        daySquare.appendChild(avisoDiv)
      }

      daySquare.addEventListener('click', () => openModal(dayString));

    } else {
      daySquare.classList.add('padding');

    }

    calendar.appendChild(daySquare);

  }

}

function closeModal(){
  newTarifaModal.style.display = 'none';
  deleteTarifaModal.style.display = 'none';
  backDrop.style.display = 'none';
  clicked= null;
  load();
}

function saveTarifa(){

    //subis a al events declarado arriba de todo la fecha del día que clickeaste y despues lo sube a LocalStorage
    events.push({
      date:clicked,
    })
    localStorage.setItem('events', JSON.stringify(events))
    closeModal()
  
  

}

function deleteTarifa(){
  events = events.filter(e => e.date !== clicked)
  localStorage.setItem('events', JSON.stringify(events))
  closeModal()
}

function initButtons(){
  document.getElementById('nextButton').addEventListener('click', () =>{
    //Incrementamos el mes y despues cargamos el mes nuevamente
    nav++;
    load();
  })
  document.getElementById('backButton').addEventListener('click', () =>{
    //Decrementamos el mes y despues cargamos el mes nuevamente
    nav--;
    load();
  })

  document.getElementById('saveButton').addEventListener('click', saveTarifa)
  document.getElementById('cancelButton').addEventListener('click', closeModal)

  document.getElementById('deleteButton').addEventListener('click', deleteTarifa)
  document.getElementById('closeButton').addEventListener('click', closeModal)

}

initButtons();
loadEvents();
