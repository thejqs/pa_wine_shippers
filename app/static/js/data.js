var width = document.documentElement.clientWidth;
var sumShippersLocation = document.getElementById('total-shippers');
var responseAggregateLocation = document.getElementById('sum-filtered-data');
var responseLocation = document.getElementById('filtered-data');
var allShippersLocation = document.getElementById('all-shippers');
var blackIcon = L.Icon.extend({
  options: {
      iconUrl: markerPath,
      iconSize: [24, 24]
  }
});

function County (name) {
  this.name = name;
  this.shippers = [];
  // a generator in js. how thrilling.
  this.unpacker = function* unpacker (obj) {
    for (var i = 0; i < obj.length; i++) {
      let val = obj[i];
      val = '<p>' + val + '</p>';
      yield val
    };
  }
};

function setLargeMapZoom (map) {
  map.setView([35, -150], 3)
};

function setSmallMapZoom (map) {
  map.setView([40, -75], 5)
};

function setMap () {
  L.preferCanvas = true;
  let layer = new L.StamenTileLayer('watercolor');
  let southWest = L.latLng(25, -170);
  let northEast = L.latLng(44, 12);
  let bounds = L.latLngBounds(southWest, northEast);
  let map = new L.Map('map', {maxBounds: bounds,
                              minZoom: 3,
                              scrollWheelZoom: false})
  map.addLayer(layer);
  populateData(map, shippers);
  if (width > 450) {
    setLargeMapZoom(map);
  }
  else {
    setSmallMapZoom(map);
  }
};

// function getData (map) {
//   var shippers_xhr = new XMLHttpRequest();
//   shippers_xhr.open('GET', ajaxURL, true);
//   shippers_xhr.onload = function () {
//     if (shippers_xhr.status === 200) {
//       populateData(map, shippers_xhr);
//     }
//   }
//   shippers_xhr.send()
// };

function populateData (map, data) {
  sumShippersLocation.innerHTML = data.length;
  for (let i = 0; i < data.length; i++) {
    let shipper = data[i];
    // sometimes the newest data will have a couple addresses without
    // lat and long yet. this makes sure the map and filters don't break.
    try {
      let shipperLatLong = [shipper['latitude'], shipper['longitude']];

      var marker = L.marker(
        shipperLatLong,
        {
          icon: new blackIcon()
        })
        .addTo(map);
    }
    catch (e) {
      console.log('oopsie');
    };

    let popupHtml = '<h2>' +
                    shipper['name'] +
                    '</h2>';

    popupHtml += '<h4>' +
                 shipper['api_address'] +
//                 ' // ' +
//                 shipper['email'].toLowerCase() +
                 ' // ' +
                 shipper['phone'] +
                 '</h4>';

    marker.bindPopup(popupHtml);
  }
};

setMap()

function addStates(shippers) {
  let states = new Set();
  for (let i = 0; i < shippers.length; i++) {
    let possibleUnique = shippers[i];
    if (!(possibleUnique['state_long'] in states) && width > 450) {
      if (possibleUnique['state_long']) {
        states.add(possibleUnique['state_long']);
      }
      else {
        states.add(possibleUnique['country']);
      }
    }
    else {
      if (possibleUnique['state_short']) {
        states.add(possibleUnique['state_short']);
      }
      else {
        states.add(possibleUnique['country']);
      }
    }
  }
  states = Array.from(states).sort();
  states.forEach(function (v, idx) {
    document.getElementById('states').innerHTML += '<option>' +
                                                   v +
                                                   '</option>';
  });
}

addStates(shippers)

function reset () {
  allShippersLocation.style.display = 'none';
  responseAggregateLocation.innerHTML = '';
  responseLocation.innerHTML = '';
}

function getStateData (state, shippers) {
  let stateShippers = [];
  for (let i = 0; i < shippers.length; i++) {
    let shipper = shippers[i];
    if (shipper.state_long == state || shipper.state_short == state
          || shipper.country == state) {
      stateShippers.push(shipper);
    };
  };
  responseLocation.innerHTML = '';
  allShippersLocation.style.display = 'none';
  responseAggregateLocation.innerHTML = '<div class="shipper">' +
                                        'Found ' +
                                        stateShippers.length +
                                        ' for ' +
                                        state +
                                        '</div>';
  if (stateShippers.length > 0) {
    stateShippers.forEach(function (v, idx) {

      // annoyingly, trying simply to set conditionally the one line
      // that changes means the broswer closes the open div at that point
      // and any styling is lost. worth coming back to later.
      if (v['api_address']) {
        responseLocation.innerHTML += '<div class="shipper">' +
                                      '<h3>' + v['name'] + '</h3>' +
                                      '<p>' + v['county'] + '</p>' +
                                      '<p>' + v['api_address'] + '</p>' +
//                                      '<p>' + v['email'].toLowerCase() + '</p>' +
                                      '<p>' + v['phone'] + '</p>' +
                                      '</div>';
      }
      else {
        responseLocation.innerHTML += '<div class="shipper">' +
                                      '<h3>' + v['name'] + '</h3>' +
                                      '<p>' + v['raw_address'] + '</p>' +
//                                      '<p>' + v['email'].toLowerCase() + '</p>' +
                                      '<p>' + v['phone'] + '</p>' +
                                      '</div>';
      }
    });
  }
  else {
    responseLocation.innerHTML = '<div class="shipper">' +
                                 "Nothing there, bub. Sorry." +
                                 '</div>'
  }
}

function showAllShippers () {
  responseLocation.innerHTML = '';
  responseAggregateLocation.innerHTML = '';
  let shown = false;
  if (shown === false) {
    allShippersLocation.style.display = 'inline-block';
    shown = true;
    return
  }
}

function dominantShipper (shippers) {
  let text1 = "There are "
  // cheating for now because I know the answer and because it will
  // be the answer for quite some time.
  let text2 = " in California -- "
  let text3 = " percent of the total."
  let dominantTotal = 0;
  for (let i = 0; i < shippers.length; i++) {
    let cali = shippers[i];
    if (cali['state_long'] === 'California') {
      dominantTotal++
    }
  }
  let dominantPercentage = ((dominantTotal / shippers.length) * 100).toFixed(2)
  document.getElementById('california-dominant').innerHTML = text1 +
                                                             '<strong>' + dominantTotal + '</strong>' +
                                                             text2 +
                                                             '<strong>' + dominantPercentage + '</strong>' +
                                                             text3
}

dominantShipper(shippers)
