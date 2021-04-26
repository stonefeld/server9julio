var fields = document.getElementById('fields');
var add = document.getElementById('add');
var remove = document.getElementById('remove');

add.onclick = function(){
    var newField = document.createElement('input');
    newField.setAttribute('type', 'number');
    newField.setAttribute('name', 'valor');
    newField.setAttribute('class', 'fields');
    newField.setAttribute('siz', 50 );
    newField.setAttribute('placeholder', 'sadsda');
    fields.appendChild(newField);
}

remove.onclick = function(){
    var input_tags = fields.getElementsByTagName('input');
    if(input_tags.length >2){
        fields.removeChild(input_tags[(input_tags.length)-1]);


    }


}
var valorTarifaNormal= document.getElementById('valorTarifaNormal');
function addTarifa(){
    var newValorTarifaNormal= document.createElement('input');
    newField.setAttribute('type', 'number');
    newField.setAttribute('id', 'valorTarifaNormal');
    newField.setAttribute('class', 'form-control');
    newField.setAttribute('placeholder', '00.00');
    fields.appendChild(newValorTarifaNormal);
}

function removeTarifa(){


}


