



// get position coordinates 
const get_location = (call_back)=>{
    if (navigator.geolocation){
        console.log('works')
        navigator.geolocation.getCurrentPosition((position)=>{
            console.log(position)
            let lat = position.coords.latitude
            call_back(position.coords.longitude,position.coords.latitude)
        })
     
        
    }   
}





const ge_posiCoordinates = (longi,lati) =>{
    console.log('longitude->',longi,'latitiude->',lati)
    // calling fetch weather from here because of call_back pattern 
    
    url = new Request('/get_location/')
    const coordinates = {
        longitude :longi,
        latitude :lati
    }

    const header = new Headers({ 'Content-Type': 'application/json'})
    fetch(
        url,
        {
            method: 'POST',
            header,
            body:JSON.stringify(coordinates)
        }

    ).then((response)=> response.json()).then((data) => {
        console.log(data)
        console.log(data.address.city)
        const city_name = data.address.city
        document.cookie = 'city_name='+ JSON.stringify(city_name)+';'+'path=/'
    })
}

// customzie cards


get_location(ge_posiCoordinates);