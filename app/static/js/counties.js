function getCountyData (shippers) {
  var countyShippers = new Set();
  for (var i = 0; i < shippers.length; i++) {
    var shipper = shippers[i];
    var fullCountyName = shipper['county'] + ', ' + shipper['state'];
    if (!(fullCountyName in countyShippers)) {
      countyShippers.add(fullCountyName);
    }
  }
  var counties = new Set();
  countyShippers.forEach(function (v, idx) {
    var county = new County(v);
    for (i = 0; i < shippers.length; i++) {
      var single = shippers[i];
      if (single['county'] + ', ' + single['state'] === county.name) {
        county.shippers.push([single['name'],
                       single['address'],
                       single['phone'],
                       single['email']]);
      }
    }
    counties.add(county);
  });
  responseLocation.innerHTML = '';
  if (counties.size > 0) {
    counties.forEach(function (v, idx) {
      responseLocation.innerHTML += '<h3>' +
                                    v['name'] +
                                    '</h3>';
      // let x = [...v.unpacker(v.shippers)];
      for (let y of v.shippers) {
        responseLocation.innerHTML += '<p>' + y + '</p>';
      }
    });
  } else {
    responseLocation.innerHTML = '<div class="shipper">' +
                                 "Nothing there, bub. Sorry." +
                                 '</div>'
  }
}
