const backDrop = document.getElementById('modalBackDrop');
const CierreCaja = async () => {
    try {
        const res = await fetch(`/estacionamiento/cierre-caja`);
        const recauadado = await res.json();
        console.log('Dentro del boton');
        console.log(recauadado);
        openModalCaja(recauadado);
    } 
    catch (err){
        const recauadado = 'Error Fatal';
        openModalCaja(recauadado);
    }
    
  };

const openModalCaja = (recauadado) => {
    document.getElementById('fechaTarifaEspecial').innerText = recauadado.find(e => e.recaudacion > 0);
    newTarifaModal.style.display = 'block';
    backDrop.style.display = 'block';
}

function openModal(date){
    clicked = date;
    const tarifaEspecialForDay = events.find;
    (e => e.date === clicked);
  
    if(tarifaEspecialForDay){
      document.getElementById('fechaTarifaEspecial').innerText = tarifaEspecialForDay.date;
      deleteTarifaModal.style.display = 'block';
    }else{
      newTarifaModal.style.display = 'block';
    }
  
    backDrop.style.display = 'block';
}


function closeModal(){
    newTarifaModal.style.display = 'none';
    deleteTarifaModal.style.display = 'none';
    backDrop.style.display = 'none';
}


function initButtons(){
    document.getElementById('cierre-caja').addEventListener('click', () =>{
        CierreCaja();
    })
    document.getElementById('emitir-resumen').addEventListener('click', () =>{
        
    })
  
    document.getElementById('cancelButton').addEventListener('click', closeModal)
  
    document.getElementById('closeButton').addEventListener('click', closeModal)
  
  }
  
  initButtons();