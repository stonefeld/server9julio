import {isWeekend, getDayName} from "./date-helper.js";

const calendar  = document.querySelector("#app-calendar");

for(let day= 1; day <= 31; day ++){
    
    const weekend = isWeekend(day);

    let name = "";

    if(day <= 7){
        const dayName = getDayName(day)
        name = `<div class="name">${dayName}</div`>;
    }

    calendar.insertAdjacentHTML("beforeend", `<div 
    class="day ${weekend ? "weekend" : ""}">${name}${day}</div>`);

}

document.querySelectorAll("#app-calendar.day").forEach;
(day =>{
    day.addEventListener("click", event => {
        event.currentTarget.classList.toggle("selected")
    })
})