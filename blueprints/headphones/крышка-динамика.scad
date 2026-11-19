// Крышка Ø70, динамик 40×17. z=0 — наружная плоскость обода, пеньки в +z.
$fn = 96;

od = 70;
rim_t = 1.8;
stack = 8.5;
boss_h = stack - rim_t;
rebate_h = 0.8;
rebate_w = 2;
lip_w = 1.8 + rebate_w;
lip_h = stack - 3 + rebate_h - rim_t;
step = 1;

boss_tip = 6.3;
boss_root = 8;

cbore_d = 4.2;
cbore_h = 2;
hole_d = 2.5;
spot_d = 4.6;
spot_h = 2;
hex_af = 4;

pocket_d = 40.2;
pocket_h = 8;
floor_t = 1.8;
dome_d = 42.8;
floor_z = rim_t - pocket_h - floor_t;

cross_r = (59 - boss_tip) / 2;
tri_side = 54.2 - boss_tip;
tri_r = tri_side / sqrt(3);
tri_a = 15;

g_center_d = 8;
g_hole_n = 8;
g_hole_d = 3.05;
g_hole_r = 8.9;
g_arc_n = 4;
g_arc_r = 15.5;
g_arc_w = 4.2;
g_arc_ang = 58;
g_mid_n = 4;
g_mid_d = 4;
g_mid_r = 16.2;

eps = 0.02;

module lip() {
  translate([0, 0, rim_t])
    difference() {
      cylinder(h = lip_h, d = od);
      translate([0, 0, -eps])
        cylinder(h = lip_h + 2 * eps, d = od - 2 * lip_w);
      translate([0, 0, lip_h - rebate_h])
        difference() {
          cylinder(h = rebate_h + eps, d = od + 2 * eps);
          translate([0, 0, -eps])
            cylinder(h = rebate_h + 3 * eps, d = od - 2 * rebate_w);
        }
    }
}

module boss() {
  translate([0, 0, rim_t])
    cylinder(h = boss_h, d1 = boss_root, d2 = boss_tip);
}

module at_cross() {
  for (a = [0, 90, 180, 270])
    rotate(a) translate([cross_r, 0, 0]) children();
}

module at_tri() {
  for (i = [0:2])
    rotate(tri_a + i * 120) translate([tri_r, 0, 0]) children();
}

module round_hole() {
  translate([0, 0, stack - cbore_h])
    cylinder(h = cbore_h + eps, d = cbore_d);
  translate([0, 0, spot_h - eps])
    cylinder(h = stack - cbore_h - spot_h + 2 * eps, d = hole_d);
  translate([0, 0, -eps])
    cylinder(h = spot_h + eps, d = spot_d);
}

module hex_hole() {
  translate([0, 0, -eps])
    cylinder(h = stack + 2 * eps, d = hex_af / cos(30), $fn = 6);
}

module arc_slot(r, w, ang) {
  rotate_extrude(angle = ang)
    translate([r - w / 2, floor_z - eps])
      square([w, floor_t + 2 * eps]);
}

module grille() {
  translate([0, 0, floor_z - eps])
    cylinder(h = floor_t + 2 * eps, d = g_center_d);
  for (i = [0:g_hole_n - 1])
    rotate(i * 360 / g_hole_n)
      translate([g_hole_r, 0, floor_z - eps])
        cylinder(h = floor_t + 2 * eps, d = g_hole_d);
  for (i = [0:g_mid_n - 1])
    rotate(i * 360 / g_mid_n + 45)
      translate([g_mid_r, 0, floor_z - eps])
        cylinder(h = floor_t + 2 * eps, d = g_mid_d);
  for (i = [0:g_arc_n - 1])
    rotate(i * 360 / g_arc_n - g_arc_ang / 2)
      arc_slot(g_arc_r, g_arc_w, g_arc_ang);
}

difference() {
  union() {
    cylinder(h = rim_t, d = od);
    translate([0, 0, floor_z])
      cylinder(h = -floor_z, d = dome_d);
    lip();
    at_cross() boss();
    at_tri() boss();
  }
  translate([0, 0, rim_t - pocket_h + step])
    cylinder(h = pocket_h - step + eps, d = pocket_d);
  translate([0, 0, rim_t - pocket_h - eps])
    cylinder(h = step + 2 * eps, d = pocket_d - 2 * step);
  grille();
  at_cross() round_hole();
  at_tri() hex_hole();
}
