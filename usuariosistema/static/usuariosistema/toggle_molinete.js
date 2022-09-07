const toggleMolinete = document.getElementById('toggle-molinete')
var molinete = document.getElementById('molinete')

toggleMolinete.addEventListener('click', (e) => {
  if (molinete.value == 1) {
    e.target.innerHTML = 'Molinete 2'
    molinete.value = 2
  } else if (molinete.value == 2) {
    e.target.innerHTML = 'Molinete 1'
    molinete.value = 1
  }
})
