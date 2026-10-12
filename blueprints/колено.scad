// Колено 90°, канализация. Печать: АБС.
// Выход вниз Ø102 наружный — вклейка в трубу без раструба, торец трубы вровень с полом.
// Вход слева Ø110 внутренний. Клей: стекольный автомобильный герметик.
$fn = 96;

inlet_id = 110;
wall = 3.5;
inlet_od = inlet_id + 2 * wall;
outlet_od = 102;
outlet_id = outlet_od - 2 * wall;

inlet_straight = 57;
outlet_x = 122;
outlet_y0 = -69;
outlet_end = -130;

flange_od = 127;
flange_back = 18.3;
rf_h = 1.5;

groove_x = 4.1;
groove_len = 11.6;
groove_depth = 4.9;
groove_d = inlet_id + 2 * groove_depth;

disk_h = 0.4;
cut_extra = 1;

ir = inlet_od / 2;
orad = outlet_od / 2;
// Сечение: наружная точка, точка на противоположной стенке.
profile = [
  [[inlet_straight, ir], [inlet_straight, -ir]],
  [[102, 37], [59, -ir]],
  [[143, 11], [outlet_x - orad, outlet_y0]],
  [[outlet_x + orad, -45], [outlet_x - orad, outlet_y0]],
  [[outlet_x + orad, outlet_y0], [outlet_x - orad, outlet_y0]]
];

function vsub(a, b) = [a[0] - b[0], a[1] - b[1]];
function vlen(a) = sqrt(a[0] * a[0] + a[1] * a[1]);
function pmid(a, b) = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];

module station(outer, inner, shrink = 0) {
  d = vsub(outer, inner);
  f1 = [d[1], -d[0]];
  f2 = [-d[1], d[0]];
  f = (f1[0] - f1[1] >= f2[0] - f2[1]) ? f1 : f2;
  translate([pmid(outer, inner)[0], pmid(outer, inner)[1], 0])
    rotate([0, 0, atan2(f[1], f[0])])
    rotate([0, 90, 0])
    cylinder(r = vlen(d) / 2 - shrink, h = disk_h, center = true);
}

module sweep(shrink = 0) {
  for (i = [0:len(profile) - 2])
    hull() {
      station(profile[i][0], profile[i][1], shrink);
      station(profile[i + 1][0], profile[i + 1][1], shrink);
    }
}

module outer_body() {
    translate([2, 0, 0])
  rotate([0, 90, 0])
    cylinder(h = inlet_straight, r = ir);
  translate([outlet_x, outlet_y0, 0])
    rotate([90, 0, 0])
    cylinder(h = outlet_y0 - outlet_end, r = orad);
  sweep(0);
  translate([rf_h, 0, 0])
    rotate([0, 90, 0])
    cylinder(h = flange_back - rf_h, r = flange_od / 2);
}

module bore() {
  translate([-cut_extra, 0, 0])
    rotate([0, 90, 0])
    cylinder(h = inlet_straight + cut_extra, r = inlet_id / 2);
  translate([outlet_x, outlet_y0, 0])
    rotate([90, 0, 0])
    cylinder(h = outlet_y0 - outlet_end + cut_extra, r = outlet_id / 2);
  sweep(wall);
  translate([groove_x, 0, 0])
    rotate([0, 90, 0])
    cylinder(h = groove_len, r = groove_d / 2);
}

difference() {
  outer_body();
  bore();
}
