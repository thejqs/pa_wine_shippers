var ajaxURL = 'https://s3.us-east-2.amazonaws.com/pa-wine-shippers/wine_shippers-2017-01-14.json';
var blackIcon = L.Icon.extend({
    options: {
        iconUrl: markerPath,
        iconSize: [24, 24]
    }
});

function setMap () {
  L.preferCanvas = true;
  var layer = new L.StamenTileLayer('watercolor');
  var southWest = L.latLng(32, -117);
  var northEast = L.latLng(44, -66);
  var bounds = L.latLngBounds(southWest, northEast);
  var map = new L.Map('map', {maxBounds: bounds})
        .setView([40, -99], 4);
  map.addLayer(layer);
  getData(map);
};

function getData (map) {
  var shippers_xhr = new XMLHttpRequest();
  shippers_xhr.open('GET', ajaxURL, true);
  shippers_xhr.onload = function () {
    if (shippers_xhr.status === 200) {
      populateMap(map, shippers_xhr);
    }
  }
  shippers_xhr.send()
};

function populateMap(map, shippers_xhr) {
  var shippers = JSON.parse(shippers_xhr.responseText);
  for (var i = 0; i < shippers.length; i++) {
    var shipper = shippers[i];
    var shipperLatLong = [shipper['latitude'], shipper['longitude']];

    var marker = L.marker(
      shipperLatLong,
      {
        icon: new blackIcon()
      })
      .addTo(map);

    var popupHtml = '<h2>' +
                    shipper['name'] +
                    '</h2>';
    popupHtml += '<h4>' +
                 shipper['address'] +
                 ' // ' +
                 shipper['email'] +
                 ' // ' +
                 shipper['phone'] +
                 '</h4>';

    marker.bindPopup(popupHtml)
  }
};

setMap()
