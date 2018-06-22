//The not nearly as nice saliens.js!
var serverCtx = new CServerInterface();
serverCtx.Connect(function(){
    console.log("Connected to server!");
    //We use this in the event the current is captured.
    function getRandomZone(planet, callback){
        serverCtx.GetPlanet(planet, function(res){
            for(var i=0;i<res.response.planets[0].zones.length;i++){
                if(res.response.planets[0].zones[i].captured==false){
                    callback(i);
                    return;
                }
            }
        });
    }
    serverCtx.GetPlayerInfo(function(res){
        var activePlanet = res.response.active_planet;
        //Master loop, this runs once every 150 seconds.
        //This needs to be delayed by at least 120 seconds(2 minutes) which is
        //the duration of one round. We insert a 15 second delay to simulate loading.
        setInterval(function(){
            //Report our "score"
            console.log("Reporting score");
            serverCtx.ReportScore(2000+Math.round(Math.random()*300), function(res){
                if(res){
                    if(!("response" in res))return;
                    if(!("new_score" in res.response)) return;
                    console.info("Current score: "+res.response.new_score+"/"+res.response.next_level_score+"; Current level: "+res.response.new_level);
                    //Insert stuff to do with your score here.
                }
            }, console.error); //idk dump errors to console?
            
            //Wait about 10-15 seconds and join a new zone
            setTimeout(function(){
                //JoinZone is to join a tile, this is needed before we can report score.
                //Since the server seems to be 502 internal server erroring, we don't rely on success callback.
                console.log("Choosing zone...");
                getRandomZone(activePlanet, function(id){
                    console.log("Chose zone "+id);
                    serverCtx.JoinZone(id, console.log, console.error);
                });
            }, Math.floor(Math.random()*5000)+10000);
        },150000);
        
        setTimeout(function(){
            console.log("Choosing zone...");
            getRandomZone(activePlanet, function(id){
                console.log("Chose zone "+id);
                serverCtx.JoinZone(id, console.log, console.error);
            });
        },Math.floor(Math.random()*5000)+5000);
    });
});
