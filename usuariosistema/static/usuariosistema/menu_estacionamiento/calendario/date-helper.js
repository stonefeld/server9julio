const isWeekend = day =>{
    //6 hace referencia a los sab, 0 a dom
    return day % 7 === 0 || day % 7 ===6;
}

const getDayName = day => {

    /*Ojo aca porque esto esta Hardcodeado y no es
      recomendable, porque necesitas que tome el dia que tenes en tu pc
      no uno que le pasas     
    */
    const date = new Date(Date.UTC(2018,0,day));

    const dayName = new Intl.DateTimeFormat("es",{weekday: "short"}).format(date);

}

export {isWeekend}