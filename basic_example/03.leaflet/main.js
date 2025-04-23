// First we’ll initialize the map and set its view to our chosen geographical coordinates and a zoom level
var map = L.map("map").setView([-22.875811, -43.214353], 13);

// Add a  tile layer to add to our map
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
        '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

//  You can easily add other things to your map
// Markers
var marker = L.marker([-22.875811, -43.214353]).addTo(map);
var markerTwo = L.marker([-22.875811, -43.234353]).addTo(map);
// Circles
var circle = L.circle([-22.875811, -43.214353], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: 500
}).addTo(map);
// Polylines, polygons
var polygon = L.polygon([
    [-22.875811, -43.214353],
    [-22.875811, -43.234353],
    [-22.885811, -43.214353]
]).addTo(map);
// Popups
marker.bindPopup("<b>Hello world!</b><br>I am a popup.").openPopup();
markerTwo.bindPopup("<b>Second marker</b>");
circle.bindPopup("I am a circle.");
polygon.bindPopup("I am a polygon.");

var popup = L.popup()
    .setLatLng([-23.5351223, -46.635393])
    .setContent("Trying to draw your path")
    .openOn(map);
var latlngs = [
    [-23.535370699999966, -46.635436399999925],
    [-23.53497840000004, -46.635321100000006],
    [-23.53486800000004, -46.63528970000001],
    [-23.534794400000038, -46.635226200000005],
    [-23.534735099999946, -46.63521300000005],
    [-23.535004899999976, -46.63415510000006],
];

var polyline = L.polyline(latlngs, { color: 'red' }).addTo(map);