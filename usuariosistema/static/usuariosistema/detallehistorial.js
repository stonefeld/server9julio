const deleteTarifaModal = document.getElementById('deleteTarifaModal');
const backDrop = document.getElementById('modalBackDrop');

function closeModal(){
    newTarifaModal.style.display = 'none';
    deleteTarifaModal.style.display = 'none';
    backDrop.style.display = 'none';
}

function openModalCobrar(){
    if(tarifaEspecialForDay) {
        deleteTarifaModal.style.display = 'block';
    } else {
        newTarifaModal.style.display = 'block';
    }
    backDrop.style.display = 'block';
}

function initButtons(){
    document.getElementById('')
    document.getElementById('deleteButton').addEventListener('click', deleteTarifa);
    document.getElementById('closeButton').addEventListener('click', closeModal);
    document.getElementById('cobrar').addEventListener('click', openModalCobrar);
    document.getElementById('pagarDeuda').addEventListener('click', openModalDeuda);
}

initButtons();
