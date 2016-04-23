var polling_places_api = (function(){

    var self = {

        config: {
            text_field_id: 'id_polling_location_display',
            hidden_input_id: 'id_polling_location',
            'geo_link': 'geolocationLink',
        },

        init: function(){
            self.bind();
            return self;
        },

        bind: function(){
            document.getElementById(self.config.text_field_id).addEventListener('keypress', self.handleTextSearch);
            document.getElementById(self.config.geo_link).addEventListener('click', self.handleGeolocation);
        },

        handleGeolocation: function(e){
            e.preventDefault();
            navigator.geolocation.getCurrentPosition(self.geolocateSuccess, self.geolocateFailure);
        },

        geolocateSuccess: function(position){
            self.doPollingLocationsLookup('lat=' + position.coords.latitude + '&lng=' + position.coords.longitude)
        },

        doPollingLocationsLookup: function(qs){
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/polling-places/lookup?' + qs);
            xhr.send(null);
            xhr.onreadystatechange = function(){
                var DONE = 4, OK = 200;
                if(xhr.readyState == DONE && xhr.status == OK){
                    self.populatePollingLocations(xhr);
                }
            };
        },

        handleTextSearch: function(e){
            clearTimeout(self.textTimeout);
            self.textTimeout = setTimeout(function(){
                self.doPollingLocationsLookup('q=' + encodeURIComponent(e.target.value));
            }, 300);
        },

        populatePollingLocations: function(xhr){
            var response = JSON.parse(xhr.responseText);

            document.getElementById('polling_locations_list').innerHTML = '';

            var tpl = document.getElementById('pp_template');
            if(response.length){
                for(var p = 0; p < response.length; p++){
                    var _tpl = tpl.cloneNode(true);
                    _tpl.removeAttribute('id');
                    _tpl.removeAttribute('style');
                    _tpl.setAttribute('data-precinctid', response[p]['precinctid']);
                    for(var e in response[p]){
                        var elem = _tpl.querySelector('*[data-bind="' + e + '"]');
                        if(elem){
                            elem.innerHTML = response[p][e];
                        }
                    }
                    document.getElementById('polling_locations_list').appendChild(_tpl);
                    _tpl.addEventListener('click', self.setPollingLocation);
                }
            } else {
                var _tpl = tpl.cloneNode();
                _tpl.removeAttribute('id');
                _tpl.removeAttribute('style');
                _tpl.innerHTML = 'No results found.'
                document.getElementById('polling_locations_list').appendChild(_tpl);
            }

            document.getElementById('polling_locations_list').removeAttribute('style');

        },

        setPollingLocation: function(e){
            e.preventDefault();
            document.getElementById(self.config.hidden_input_id).value = e.target.parentNode.parentNode.getAttribute('data-precinctid');
            document.getElementById(self.config.text_field_id).value = e.target.parentNode.innerText;
            document.getElementById('polling_locations_list').setAttribute('style', 'display: none;');
        },

        geolocateFailure: function(){
            // alert('fail');
        }

    };


    return self.init();

})();