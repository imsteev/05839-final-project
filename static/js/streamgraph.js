chart("/static/data/streamgraph.csv", "scale");

var datearray = [];
var colorrange = [];


function chart(csvpath, color) {

    if (color == "blue") {
        colorrange = ["#045A8D", "#2B8CBE", "#74A9CF", "#A6BDDB", "#D0D1E6", "#F1EEF6"];
    }
    else if (color == "pink") {
        colorrange = ["#980043", "#DD1C77", "#DF65B0", "#C994C7", "#D4B9DA", "#F1EEF6"];
    }
    else if (color == "orange") {
        colorrange = ["#B30000", "#E34A33", "#FC8D59", "#FDBB84", "#FDD49E", "#FEF0D9"];
    }
    else if (color == "scale") {
        //   var color = d3.scaleSequential(d3.interpolateInferno).domain([0, 30]); this is v4 up
        var color = d3.scale.linear().domain([0, 5]).range(["#FC8D59", "#C994C7"])
        var foo = new Array(15);

        var colorrange = [];

        for (var i = 0; i < foo.length; i++) {
            colorrange.push(color(i));
        }

        //   colorrange = color(20,21)


        //   var color = d3.scaleLinear().domain([10, 100]).range(["brown", "steelblue"]);
        //   colorrange = color([1,10]); // "#9a3439"
    }
    // console.log(colorrange)
    strokecolor = "#fff";
    // strokecolor = colorrange[0];


    var format = d3.time.format("%m/%d/%y");
    // var format = d3.timeParse("%m/%d/%y"); this is v2

    var margin = { top: 20, right: 60, bottom: 30, left: 60 };
    var width = document.body.clientWidth*0.72 - margin.left - margin.right;
    // var width = document.body.clientWidth - margin.left - margin.right;
    var height = 500 - margin.top - margin.bottom;

    var tooltip = d3.select(".chart")
        .append("div")
        .attr("class", "remove")
        .style("position", "relative")
        .style("z-index", "20")
        .style("visibility", "hidden")
        .style("top", "30px")
        .style("left", "55px");

    var x = d3.time.scale()
        // var x = d3.scaleTime()
        .range([0, width]);

    var y = d3.scale.linear()
        // var y = d3.scaleLinear()
        .range([height - 10, 0]);

    var z = d3.scale.ordinal()
        // var z = d3.scaleOrdinal()
        .range(colorrange);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(d3.time.years);
    // var xAxis = d3.axisBottom(x)
    //     .ticks(d3.timeYears);

    // var yAxis = d3.axisLeft(x);

    // var yAxisr = d3.axisRight(x);

    var yAxis = d3.svg.axis()
        .scale(y);

    var yAxisr = d3.svg.axis()
        .scale(y);

    var stack = d3.layout.stack()
        .offset("silhouette")
        .values(function (d) { return d.values; })
        .x(function (d) { return d.date; })
        .y(function (d) { return d.value; });

    var nest = d3.nest()
        .key(function (d) { return d.key; });

    var area = d3.svg.area()
        .interpolate("cardinal")
        .x(function (d) { return x(d.date); })
        .y0(function (d) { return y(d.y0); })
        .y1(function (d) { return y(d.y0 + d.y); });

    var svg = d3.select(".chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var graph = d3.csv(csvpath, function (data) {
        data.forEach(function (d) {
            d.date = format.parse(d.date);
            d.value = +d.value;
        });

        var layers = stack(nest.entries(data));

        x.domain(d3.extent(data, function (d) { return d.date; }));
        y.domain([0, d3.max(data, function (d) { return d.y0 + d.y; })]);

        svg.selectAll(".layer")
            .data(layers)
            .enter().append("path")
            .attr("class", "layer")
            .attr("d", function (d) { return area(d.values); })
            .style("fill", function (d, i) { return z(i); });


        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + width + ", 0)")
            .call(yAxis.orient("right"));

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis.orient("left"));

        svg.selectAll(".layer")
            .attr("opacity", 1)
            .on("mouseover", function (d, i) {
                svg.selectAll(".layer").transition()
                    .duration(250)
                    .attr("opacity", function (d, j) {
                        return j != i ? 0.5 : 1;
                    })
            })

            .on("mousemove", function (d, i) {
                // console.log('MOUSE MOVE', d, i, this)
                mousex = d3.mouse(this);
                mousex = mousex[0];
                var invertedx = x.invert(mousex);
                invertedx = invertedx.getFullYear();
                //   invertedx = invertedx.getMonth() + invertedx.getDate();
                var selected = (d.values);
                for (var k = 0; k < selected.length; k++) {
                    datearray[k] = selected[k].date
                    datearray[k] = datearray[k].getFullYear();
                    // datearray[k] = datearray[k].getMonth() + datearray[k].getDate();
                }
                // console.log("HOVER", d, i);
                mousedate = datearray.indexOf(invertedx);
                pro = d.values[mousedate].value;

                d3.select(this)
                    .classed("hover", true)
                    .attr("stroke", strokecolor)
                    .attr("stroke-width", "1px"),
                    //   tooltip.html( "<p>" + d.key + "<br>" + pro + "</p>" ).style("visibility", "visible");
                    // https://stackoverflow.com/questions/24998682/d3-interactive-stream-graph-data-repeating-past-one-month
                    tooltip.html("<p>" + d.key + "<br>" + pro + " occurences</p>").style("visibility", "visible").style("left", mousex + "px");
            })
            .on("mouseout", function (d, i) {
                svg.selectAll(".layer")
                    .transition()
                    .duration(250)
                    //   .duration(250)
                    .attr("opacity", "1")
                    .attr("stroke-width", "0.2px");
                d3.select(this)
                    .classed("hover", false)
                    .attr("stroke-width", "0px"), tooltip.html("<p>" + d.key + "<br>" + pro + " occurenes</p>").style("visibility", "visible");
            })

        var vertical = d3.select(".chart")
            .append("div")
            .attr("class", "remove")
            .style("position", "relative")
            .style("z-index", "19")
            .style("width", "1px")
            .style("height", "480px")
            .style("top", "-500px")
            // .style("bottom", "200px")
            .style("left",  "0px")
            .style("background", "#fff");

        // var vertical = d3.select(".chart")
        //         .append("hr")
        //         .attr("class","remove")
        //         .attr("width","1")
        //         .attr("size",500)
        //         .style("z-index", "19")
        //         .style("background", "#fff");

        d3.select(".chart")
            .on("mousemove", function () {
                mousex = d3.mouse(this);
                console.log(mousex)
                mousex = mousex[0] + 5;
                vertical.style("left", mousex + "px")
            })
            .on("mouseover", function () {
                mousex = d3.mouse(this);
                mousex = mousex[0] + 5;
                vertical.style("left", mousex + "px")
            });
    });
}