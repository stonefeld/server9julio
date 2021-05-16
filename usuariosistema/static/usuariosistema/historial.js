function openNav() {
  document.getElementById('mySidebar').style.width = '250px';
  document.getElementById('main').style.marginLeft = '250px';
  document.getElementById('openbtn').style.display = 'none';
  var caret = document.getElementsByClassName('caret');
  setTimeout(() => {
    for (i = 0; i < caret.length; i++) {
      caret[i].style.display = 'block';
    }
  }, 250);
}

function closeNav() {
  var caret = document.getElementsByClassName('caret');
  for (i = 0; i < caret.length; i++) {
    caret[i].style.display = 'none';
  }
  document.getElementById('mySidebar').style.width = '0';
  document.getElementById('main').style.marginLeft = '0';
  document.getElementById('openbtn').style.display = 'block';
}

var dropdown = document.getElementsByClassName('dropdown-btn');
var i;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener('click', function() {
    this.classList.toggle('active');
    var dropdownContent = this.nextElementSibling;
    
    if (dropdownContent.style.display === 'block') {
      dropdownContent.style.display = 'none';
    } else {
      dropdownContent.style.display = 'block';
    }
  });
}
