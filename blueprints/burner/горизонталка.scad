// === ПАРАМЕТРЫ УСТРОЙСТВА ===
$fn = 60;

wall = 3;               // Толщина стенок металла
sq_size = 100;          // Размер квадратной трубы
sq_len = 180;           // Длина квадратной трубы
r_diam = 90;            // Диаметр круглой трубы
r_len = 100;            // Длина круглой трубы
trans_len = 50;         // Длина перехода квадрат->круг

// Параметры фланца и окна
flange_diam = 250;      // Диаметр фланца
flange_thick = 8;       // Толщина фланца
window_diam = 35;       // Диаметр смотрового окна

// Смещение конструкции вниз относительно окна
body_shift_y = -22;     

// ПАРАМЕТРЫ ЦИКЛОННОЙ ЗОНЫ (СТРОГО НА КРУГЛОЙ ТРУБЕ)
hole_diam = 2.5;        // Диаметр отверстий 2.5мм
num_holes = 25;         // 25 штук в один ряд
cyclone_angle = 35;     // Угол закрутки потока

// ВАШЕ УСЛОВИЕ: Конус продлен от фланца до точки +5мм после отверстий
jacket_start_d = 160;   // Большой диаметр, соединенный с фланцем
jacket_len = trans_len + 9; // Длина конуса до перекрытия (+5мм после отверстий)

// Параметры нижнего воздуховода
air_pipe_d = 50;        // Диаметр трубы подачи воздуха
box_w = 60;             // Ширина воздушного короба
box_h = 20;             // Высота короба снаружи
box_len = 110;          // Длина короба до фланца
box_z_shift = -110;     // Позиция начала короба по Z

// Габариты картриджа под квадратную трубу 100х100х160 (внутренний зазор учтен)
insert_len = 160;       // Реальная длина картриджа (160 мм)
insert_height = 94;     // Реальная высота картриджа (94 мм)
insert_width = 94;      // Реальная ширина картриджа (94 мм)

insert_thick = 1.5;     // Толщина металла внутренних пластин (1.5 мм)
plate_thick = 1.5;      // Толщина боковых стенок (1.5 мм)

cut_z = 0; 

// === СБОРКА ВСЕЙ КОНСТРУКЦИИ ===
//projection(cut = true)
difference(){
rotate([0,90,0])
union() {
    // 1. Основной сквозной тракт устройства
    translate([0, body_shift_y, 0]) {
        difference() {
            main_body_outer();
            main_body_inner();
            cyclone_row_holes();    // Отверстия на круглой трубе сразу после перехода
            bottom_air_scad_cuts2();
        }
        main_body_inner_deflector();
    }
    
    // 2. Большой фланец со смотровым окном
    difference() {
        flange_outer();
        flange_inner_cut();      
        flange_view_window();    
        flange_air_passage();    // Отверстие для воздуха сквозь фланец прямо внутрь конуса
    }
    
    // СМЕЩЕННЫЕ СИСТЕМЫ ВОЗДУХОВОДОВ И КОЖУХА
    translate([0, body_shift_y, 0]) {
        // 3. Герметичный конический кожух (от фланца до круглой трубы)
        cone_jacket();

        // 4. Нижний короб с наклонной трубой 45 градусов
        difference() {
            bottom_air_box_outer();
            bottom_air_box_inner();
            bottom_air_scad_cuts(); // Окно перетока внутрь квадрата
        }
    }

translate([0,-22,-34])
rotate([0,-90,-90])
translate([0,47,0])
inner_insert_assembly();
    
}
    translate([-500, -500, cut_z]) 
        cube([1000, 1000, 1000]); 
}

// --- Новый стабильный модуль перехода без hull() и polyhedron() ---
module transition_poly(sq_s, dia, h) {
    // Количество сегментов круга (кратно 4 для ровных углов квадрата)
    segments = ($fn > 0) ? $fn : 64; 
    
    half_s = sq_s / 2;
    r = dia / 2;
    
    // Функция для получения точек нижнего основания (идеальный квадрат)
    function get_square_pt(angle) = let(
        x = cos(angle), y = sin(angle),
        max_c = max(abs(x), abs(y))
    ) [x / max_c * half_s, y / max_c * half_s, 0];

    // Функция для получения точек верхнего основания (идеальный круг)
    function get_circle_pt(angle) = 
        [r * cos(angle), r * sin(angle), h];

    // Генерируем массив вершин
    vertices = concat(
        [for (i = [0 : segments - 1]) get_square_pt(i * 360 / segments)], // Нижний квадрат [0 .. segments-1]
        [for (i = [0 : segments - 1]) get_circle_pt(i * 360 / segments)]  // Верхний круг [segments .. 2*segments-1]
    );

    // Генерируем сетку треугольников с правильным обходом (нормали наружу)
    faces = concat(
        // Боковые стенки (состоят из двух треугольников на каждый сегмент)
        [for (i = [0 : segments - 1]) let(n = (i + 1) % segments) 
            [i, n, n + segments]
        ],
        [for (i = [0 : segments - 1]) let(n = (i + 1) % segments) 
            [i, n + segments, i + segments]
        ],
        // Нижняя крышка (квадратное основание, обход против часовой стрелки снизу)
        [[for (i = [segments - 1 : -1 : 0]) i]],
        // Верхняя крышка (круглое основание, обход по часовой стрелке сверху)
        [[for (i = [segments : 1 : segments * 2 - 1]) i]]
    );

    // Отрисовка монолитного объекта
    polyhedron(points = vertices, faces = faces, convexity = 10);
}

// === МОДУЛИ ГЕОМЕТРИИ ===

// Внешние контуры основного тракта
module main_body_outer() {
    translate([0, 0, -sq_len])
        linear_extrude(height = sq_len)
            square([sq_size, sq_size], center = true);
    
    transition_poly(sq_size, r_diam, trans_len);
    
    translate([0, 0, trans_len])
        cylinder(d = r_diam, h = r_len);
}

// Внутренние полости основного тракта
module main_body_inner() {
    translate([0, 0, -sq_len - 1])
        linear_extrude(height = sq_len + 1.1)
            square([sq_size - wall*2, sq_size - wall*2], center = true);
    
    transition_poly(sq_size - wall*2, r_diam - wall*2, trans_len);
        
    translate([0, 0, trans_len - 0.1])
        cylinder(d = r_diam - wall*2, h = r_len + 2);

}

module main_body_inner_deflector() {
    translate([0, -10, 2.5/2])
    union(){
        difference() {
                linear_extrude(height = 40, scale = 0.65)
                     square([95, 73], center = true);
              translate([0, 0, -0.1])
                linear_extrude(height = 40.2, scale = 0.63)
            square([95-3, 73-3], center = true);
        }
        difference(){
            translate([0, 3, 0])
                cube([100,80,2.5], center = true);
            cube([95-3,73-3,2.7], center = true);
        }
    }
   
}
// Внешняя часть фланца
module flange_outer() {
    translate([0, 0, -flange_thick])
        cylinder(d = flange_diam, h = flange_thick);
}

// Внутренний вырез во фланце
module flange_inner_cut() {
    translate([0, body_shift_y, -flange_thick - 1])
        linear_extrude(height = flange_thick + 2)
            square([sq_size - wall*2, sq_size - wall*2], center = true);
}

// Вырез под смотровое окно во фланце
module flange_view_window() {
    translate([0, flange_diam/2 - window_diam/2 - 15, -flange_thick - 1])
        cylinder(d = window_diam, h = flange_thick + 2);
}

// Отверстие во фланце для перетока воздуха из нижнего короба прямо в конус
module flange_air_passage() {
    translate([0, body_shift_y - sq_size/2 - 8, -flange_thick - 1])
        cylinder(d = 18, h = flange_thick + 2);
}

// ВАШЕ УСЛОВИЕ: Отверстия идут сразу после перехода на круглой трубе (Z=54)
module cyclone_row_holes() {
    z_pos = trans_len + 4; // Начало круглой трубы + 4мм
    
    for (i = [0 : num_holes-1]) {
        angle = i * (360 / num_holes);
        rotate([0, 0, angle])
        translate([r_diam/2 - wall, 0, z_pos])
        rotate([0, 90, cyclone_angle]) 
            cylinder(d = hole_diam, h = wall * 4, center = true);
    }
}

// ВАШЕ УСЛОВИЕ: Глухой конус соединен с фланцем (Z=0) и закрывается на круглой трубе
module cone_jacket() {
    difference() {
        // Конус плавно идет от фланца (Z=0) до конца зоны перфорации
        cylinder(d1 = jacket_start_d, d2 = r_diam, h = jacket_len + wall*2);
        
        // Внутренний вырез полости воздуха внутри конуса
        translate([0, 0, -0.1])
            cylinder(d1 = jacket_start_d - wall*2, d2 = r_diam, h = jacket_len + 0.2);
            
        translate([0, 0, trans_len - 0.1])
            cylinder(d = r_diam, h = jacket_len);
    }
}

// Внешние контуры нижнего короба и наклонной трубы
module bottom_air_box_outer() {
    translate([-box_w/2, -sq_size/2 - box_h, box_z_shift])
        cube([box_w, box_h, box_len]);

difference(){        
    translate([0, -sq_size/2 - box_h, -120])
        rotate([-45, 0, 0]) 
        translate([0, -40, 0])
            cylinder(d = air_pipe_d, h = 65);

    translate([-box_w/2 + wall, -sq_size/2 - box_h + 17, box_z_shift])
            cube([box_w, box_h, box_len]);
}
}

// Внутренние полости нижнего короба и трубы
module bottom_air_box_inner() {
    translate([-box_w/2 + wall, -sq_size/2 - box_h + wall, box_z_shift + 2])
        cube([box_w - wall*2, box_h, box_len - 2]);
    
    difference(){
    translate([0, -sq_size/2 - box_h, -122])
        rotate([-45, 0, 0]) 
        translate([0, -42, -1.5])
            cylinder(d = air_pipe_d - wall*2, h = 64);

    translate([-box_w/2 + wall, -sq_size/2 - box_h + 17, box_z_shift])
            cube([box_w, box_h, box_len]);
    }
}

// Окно перетока из короба внутрь квадратной трубы
module bottom_air_scad_cuts() {
    translate([-box_w/2 + wall*2, -sq_size/2 + wall, box_z_shift + wall])
        cube([box_w - wall*4, wall + 2, box_len - wall*2]);
}

// Окно перетока из короба внутрь квадратной трубы
module bottom_air_scad_cuts2() {
    translate([-box_w/2 + wall*2, -sq_size/2-wall, -20])
        cube([box_w - wall*4, 10, 10]);
}


// === ГЕОМЕТРИЧЕСКИЕ МОДУЛИ ===

module inner_insert_assembly() {
  scale([1.1,1,1])
    translate([-insert_width/2*1.05, 0, 0]) {
        
        // Поворот строго rotate()
        rotate([90, 0, 0]) {
            difference(){
            // Сдвигаем всё в центр локальных координат для идеального вращения
            translate([-insert_len/2, -insert_height/2, 0]) {
                
                // 1. Пять внутренних рабочих пластин (ширина 94 мм)
                  linear_extrude(height = insert_width)
                    color_sheets_2d_real();
                //}
                
                // 2. Левая глухая боковая стенка (прямоугольник 160х94 мм)
                linear_extrude(height = plate_thick)
                    square([insert_len, insert_height]);
                
                // 3. Правая глухая боковая стенка (прямоугольник 160х94 мм)
                translate([0, 0, insert_width - plate_thick])
                    linear_extrude(height = plate_thick)
                        square([insert_len, insert_height]);
            }
            
            translate([insert_width/2 + 19,-insert_width/2+1,insert_height/2])
                cube([15,3,70],center=true);
            }
        }
    
  }
}

// 2D Профиль внутренних пластин, рассчитанный строго в реальных миллиметрах
module color_sheets_2d_real() {
    t = insert_thick;
    h = insert_height; // 94 мм
    l = insert_len;    // 160 мм
    
    // 1. ГРЯЗНО-ЖЕЛТАЯ ЛИНИЯ (Верхний пологий завихритель)
    draw_flat_segment(24, h - 33, 43, h - 49, t);
    draw_flat_segment(43, h - 49, 86, h - 49, t);
    draw_flat_segment(86, h - 49, 129, h - 40, t);
    draw_flat_segment(129, h - 40, l, h - 22, t);
    draw_flat_segment(l, h - 22, l, h - 3, t); 
    
    // 2. БОРДОВАЯ ЛИНИЯ (Идет по верхнему краю h и впритирку к синей)
    draw_flat_segment(42, h - 1.5, 21, h - 1.5, t);   
    draw_flat_segment(21, h - 1.5, 5, h - 11, t); 
    draw_flat_segment(5, h - 11, 4, h - 29, t); 
    draw_flat_segment(4, h - 29, 12, h - 47, t); 
    draw_flat_segment(12, h - 47, 23, h - 54, t); 
    draw_flat_segment(23, h - 54, 33, 37, t);     
    
    // 3. СИНЯЯ ЛИНИЯ (Идет строго по нижнему краю)
    draw_flat_segment(0, 1.5, l, 1.5, t);             
    draw_flat_segment(0, 1.5, 0, 22, t);
    draw_flat_segment(0, 22, 8, 38, t);
    draw_flat_segment(8, 38, 20, 41, t);              
    
    // 4. ЗЕЛЕНАЯ ЛИНИЯ (С ВАШЕЙ ПРАВКОЙ КОРДИНАТ)
    draw_flat_segment(17, 10, 17, 18, t);
    draw_flat_segment(17, 18, 23, 28, t);
    draw_flat_segment(23, 28, 32, 32, t); // ВАШЕ ИЗМЕНЕНИЕ
    
    // 5. ЧЕРНАЯ ЛИНИЯ (Центральные точки приподняты вверх, повторяя желтую)
    draw_flat_segment(17, 10, 43, 22, t);           
    draw_flat_segment(43, 22, 86, 22, t);           
    draw_flat_segment(86, 22, 129, 14, t);          
    draw_flat_segment(129, 14, l, 1.5, t);          
}

// Построение плоского прямоугольника square() между двумя точками
module draw_flat_segment(x1, y1, x2, y2, thickness) {
    dx = x2 - x1;
    dy = y2 - y1;
    length = sqrt(dx*dx + dy*dy);
    angle = atan2(dy, dx);
    
    translate([x1, y1])
    rotate([0, 0, angle])
    translate([0, -thickness/2])
    square([length, thickness]);
}
