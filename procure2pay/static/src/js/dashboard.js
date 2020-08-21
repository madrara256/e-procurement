odoo.define('procure2pay', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var session = require('web.session');
var rpc = require('web.rpc');
var web_client = require('web.web_client');

var QWeb = core.qweb;
var _t = core._t;

var Procure2PayDashboardMain = AbstractAction.extend(ControlPanelMixin,{
	template: 'Procure2PayDashboardMain',

	cssLibs: [
		'/web/static/lib/nvd3/nv.d3.css'
	],
	jsLibs: [
		'/web/static/lib/nvd3/d3.v3.js',
		'/web/static/lib/nvd3/nv.d3.js',
		'/web/static/src/js/libs/nvd3.js'
	],

	events: {
		'click .proc_contracts': 'contracts_trends',
		'click .proc_requests': 'requests_trends',
		'click .proc_purchases': 'purchase_trends',
		'click .proc_budgets': 'budgets_trends',
		'click .proc_stock': 'stock_trends'
	},


	init: function(parent, context) {
		this._super(parent, context);
		this.date_range = 'week';
		this.date_from = moment().subtract(1, 'week');
		this.date_to = moment();
		this.dashboard_templates = ['P2PDashboardInventory', 'P2PDashboardRequests','P2PDashboardBudgets','P2PDashboardPurchaseOrder','P2PDashboardContracts',];
		// this.rfqs = [];
		// this.purchase_orders = [];
		// this.rejected_pos = [];
		console.log('init function executing');
	},

	willStart: function() {
		var self = this;
		return $.when(ajax.loadLibs(this), this._super()).then(function() {
			return self.fetch_data();
		});
		console.log('will start function executing')
	},
	start: function(){
		var self = this;
		this.set("title", 'Dashboards');
		console.log('executing start function');
		return this._super().then(function(){
			self.update_cp();
			self.render_dashboards();
			self.render_graphs();
			self.$el.parent().addClass('oe_background_grey');
		});

	},

	render_dashboards: function(){
		var self = this;
		_.each(this.dashboard_templates, function(template){
			self.$('.o_procure_dashboard').append(QWeb.render(template, {widget: self}));
		});

	},

	render_graphs: function(){
		var self = this;
		self.render_stock_trends();
		self.render_request_trends();
		self.render_purchase_trends();
		self.render_budget_trends();
		self.render_contract_trends();
		self.render_purchase_analysis();
		self.render_department_expenditure();
	},

	fetch_data: function(){
		var self = this;

		var def1 = this._rpc({
			model: 'kola.contract',
			method: 'get_contract_details'

		}).done(function(result) {
			self.contracts_due_to_expire = result['id'];
		});

		var def2 = this._rpc({
			model: 'kola.requisition',
			method: 'get_purchase_requests'

		}).done(function(res){
			self.requests = res['requests'];
			console.log(self.requests);
		});

		var def3 = this._rpc({
			model: 'purchase.order',
			method: 'get_purchases'

		}).done(function(res2){
			self.purchases = res2['purchases'];
			console.log(self.purchases);
		});

		var def4 = this._rpc({
			model: 'budget.management',
			method: 'get_all_current_budgets'

		}).done(function(res3) {
			self.budgets = res3['budgets'];
			console.log(self.budgets);
		});

		var def5 = this._rpc({
			model: 'product.product',
			method: 'get_highest_stock_standings',

		}).done(function(results) {
			console.log('executing top items in stock');
			self.top_products = results['top_ranking_stock'];
			console.log(self.top_products);
		});

		var def6 = this._rpc({
			model:'product.product',
			method: 'get_lowest_stock_standings'

		}).done(function(res4){
			console.log('executing lowest items in stock');
			self.lowest_products = res4['lowest_ranking_stock'];
			console.log(self.lowest_products);
		});

		var def7 = this._rpc({
			model: 'stock.scrap',
			method: 'get_stock_scrap_quant',

		}).done(function(res5){
			console.log('executing top products in scrap');
			self.scrap_products = res5['scrap_ranking_stock'];
			console.log(self.scrap_products);
		});

		var def8 = this._rpc({
			model: 'kola.requisition',
			method: 'get_purchase_requests',

		}).done(function(res6){
			self.new_requests = res6['new_requests'];
		});

		var def9 = this._rpc({
			model: 'kola.requisition',
			method: 'get_purchase_requests',

		}).done(function(res7){
			self.approved_requests = res7['approved_requests'];
		});

		var def10 = this._rpc({
			model: 'kola.contract',
			method: 'get_running_contracts',

		}).done(function(res8){
			self.contracts_running = res8['contracts_running'];
		});


		return $.when(def1, def2, def3, def4, def5, def6, def7, def8, def9, def10);
	},

	on_reverse_breadcrumb: function(){
		var self = this;
		web_client.do_push_state({});
		this.update_cp();
		this.fetch_data().then(function() {
			self.$('.o_procure_dashboard').empty();
			self.render_dashboards();
			self.render_graphs();
		});
		console.log('executing breadcrumbs function');
	},



	update_cp: function(){
		var self = this;
		this.update_control_panel(
			{breadcrumbs: self.breadcrumbs}, {clear: true}
		);
		console.log('executing control panel function');
	},

	stock_trends: function(e){
		var self = this;
		e.stopPropagation();
		e.preventDefault();

		console.log('Stock link Clicked')
	},

	expenditure_trends: function(e){
		var self = this;
		e.stopPropagation();
		e.preventDefault();

		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		this.do_action({}, options)
	},

	contracts_trends: function(e){
		var self = this;
		e.stopPropagation();
		e.preventDefault();

		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		this.do_action({
			name: _t("Contracts"),
			type: 'ir.actions.act_window',
			res_model: 'kola.contract',
			view_mode: 'kanban,form,tree',
			view_type: 'form',
			views: [[false, 'kanban'], [false, 'form']],
			domain:[],
			target: 'current',
		}, options)
	},

	stock_trends: function(e){
		var self = this;
		e.stopPropagation();
		e.preventDefault();

		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,

		};
		this.do_action({
			name: _t('Stock'),
			type: 'ir.actions.act_window',
			res_model: 'product.template',
			view_mode: 'kanban,form,tree',
			view_type: 'form',
			views: [[false, 'kanban'], [false, 'form']],
			domain: [],
			target: 'current',
		}, options)
	},

	requests_trends: function(e){
			var self = this;
			e.stopPropagation();
			e.preventDefault();

			var options = {
				on_reverse_breadcrumb: this.on_reverse_breadcrumb,
			};
			this.do_action({
				name: _t('Purchase Requests'),
				type: 'ir.actions.act_window',
				res_model: 'kola.requisition',
				view_mode: 'kanban,form, tree',
				view_type: 'form',
				views: [[false, 'kanban'], [false, 'form']],
				domain:[],
				target: 'current',
			},options)
		},

	purchase_trends: function(e){
		var self = this;
		e.stopPropagation();
		e.preventDefault();

		var options = {
				on_reverse_breadcrumb: this.on_reverse_breadcrumb,
			};
		this.do_action({
			name: _t('Purchases'),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'kanban, form, tree',
			view_type: 'form',
			views: [[false, 'kanban'], [false, 'form']],
			domain:[],
			target: 'current',
		},options)

	},

	budgets_trends: function(e){
		var self = this;
		e.stopPropagation();
		e.preventDefault();

		var options = {
				on_reverse_breadcrumb: this.on_reverse_breadcrumb,
			};
		this.do_action({
			name: _t('Organization Budgets'),
			type: 'ir.actions.act_window',
			res_model: 'budget.management',
			view_mode: 'kanban,form, tree',
			view_type: 'form',
			views: [[false, 'kanban'], [false, 'form']],
			domain: [],
			target: 'current',
		}, options)
	},

	render_stock_trends: function(){
		var self = this;

	},
	render_request_trends: function(){
		var self = this;

	},

	render_budget_trends: function(){
		var self = this;
		//var color = d3.scale.category10()
		var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
		'#ffa433', '#ffc25b', '#f8e54b'];
		var color = d3.scale.ordinal().range(colors);

		rpc.query({
			model: 'budget.management',
			method: 'get_all_budget_analysis',

		}).then(function(data){
			var fData = data['budget_results'];
			var id = self.$('.budget_summary')[0];

			var barColor = '#ff618a';
			// function to handle histogram.

			function histoGram(fD){
				var hG={},    hGDim = {t: 60, r: 0, b: 30, l: 0};
				hGDim.w = 350 - hGDim.l - hGDim.r,
				hGDim.h = 200 - hGDim.t - hGDim.b;

				var hGsvg = d3.select(id).append("svg")
					.attr("width", hGDim.w + hGDim.l + hGDim.r)
					.attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
					.attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

				console.log('x-axis mapping');
				var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
					.domain(fData.map(function(d) {
						return d[0];
					}));

				console.log('add the x-axis to the histoGram');
				// Add x-axis to the histogram svg.
				hGsvg.append("g").attr("class", "x axis")
					.attr("transform", "translate(0," + hGDim.h + ")")
					.call(d3.svg.axis().scale(x).orient("bottom"));

				console.log('y-axis mapping');
				// Create function for y-axis map.
				var y = d3.scale.linear().range([hGDim.h, 0])
					.domain([0, d3.max(fData, function(d) {
						return d[1];
					})]);

				// Create bars for histogram to contain rectangles and freq labels.
				var bars = hGsvg.selectAll(".bar").data(fData).enter()
					.append("g").attr("class", "bar");

				//create the rectangles.
				bars.append("rect")
					.attr("x", function(d) { return x(d[0]); })
					.attr("y", function(d) { return y(d[1]); })
					.attr("width", x.rangeBand())
					.attr("height", function(d) { return hGDim.h - y(d[1]); })
					.attr('fill',barColor);
					//.on("mouseover",mouseover)// mouseover is defined below.
					//.on("mouseout",mouseout);// mouseout is defined below.

				//Create the frequency labels above the rectangles.
				bars.append("text").text(function(d){ return d3.format(",")(d[1])})
					.attr("x", function(d) { return x(d[0])+x.rangeBand()/2; })
					.attr("y", function(d) { return y(d[1])-5; })
					.attr("text-anchor", "middle");

				// create function to update the bars. This will be used by pie-chart.
				hG.update = function(nD, color){
					// update the domain of the y-axis map to reflect change in frequencies.
					y.domain([0, d3.max(nD, function(d) { return d[1]; })]);

					// Attach the new data to the bars.
					var bars = hGsvg.selectAll(".bar").data(nD);

					// transition the height and color of rectangles.
					bars.select("rect").transition().duration(500)
						.attr("y", function(d) {return y(d[1]); })
						.attr("height", function(d) { return hGDim.h - y(d[1]); })
						.attr("fill", color);

					// transition the frequency labels location and change value.
					bars.select("text").transition().duration(500)
						.text(function(d){ return d3.format(",")(d[1])})
						.attr("y", function(d) {return y(d[1])-5; });
					}

			return hG;
			}

			var sF = fData.map(function(d){
				return [fData.forEach(item => item[1]), fData.forEach(item => item[0])];
			});

			var hG = histoGram(sF);//create the histogram.
		});

	},

	render_purchase_trends: function(){
		var self = this;
		//var color = d3.scale.category10()
		var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
		'#ffa433', '#ffc25b', '#f8e54b'];
		var color = d3.scale.ordinal().range(colors);

		rpc.query({
			model: 'purchase.order',
			method: 'get_all_purchases_records',
		}).then(function(res) {
			var fData = res[0];
			var fstate = res[1];

			console.log('printing fData');
			console.log(fData);

			console.log('printing fstate');
			console.log(fstate);

			var id = self.$('.purchase_analysis')[0];
			var barColor = '#ff618a';

			// function to handle histogram
			function histoGram(fD){
				var hG={},    hGDim = {t: 60, r: 0, b: 30, l: 0};
					hGDim.w = 350 - hGDim.l - hGDim.r,
					hGDim.h = 200 - hGDim.t - hGDim.b;

				//create svg for histogram.
				var hGsvg = d3.select(id).append("svg")
					.attr("width", hGDim.w + hGDim.l + hGDim.r)
					.attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
					.attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

				console.log('Creating x -axis');
				// create function for x-axis mapping.
				var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
						.domain(fData.map(function(d) {
							console.log('x-axis values');
							console.log(d[0]);
							return d[0];
							 }));

				console.log('Adding x -axis');
				// Add x-axis to the histogram svg.
				hGsvg.append("g").attr("class", "x axis")
					.attr("transform", "translate(0," + hGDim.h + ")")
					.call(d3.svg.axis().scale(x).orient("bottom"));

				console.log('Creating y -axis');
				// Create function for y-axis map.
				var y = d3.scale.linear().range([hGDim.h, 0])
					.domain([0, d3.max(fData, function(d) {
						console.log('y-axis values');
						console.log(d[1]);
						return d[1];
					})]
					);

				console.log('CreatinG BARS');
				// Create bars for histogram to contain rectangles and freq labels.
				var bars = hGsvg.selectAll(".bar").data(fData).enter()
					.append("g").attr("class", "bar");

				//create the rectangles.
				bars.append("rect")
					.attr("x", function(d) { return x(d[0]); })
					.attr("y", function(d) { return y(d[1]); })
					.attr("width", x.rangeBand())
					.attr("height", function(d) { return hGDim.h - y(d[1]); })
					.attr('fill',barColor)
					.on("mouseover",mouseover)// mouseover is defined below.
					.on("mouseout",mouseout);// mouseout is defined below.

				//Create the frequency labels above the rectangles.
				bars.append("text").text(function(d){ return d3.format(",")(d[1])})
					.attr("x", function(d) { return x(d[0])+x.rangeBand()/2; })
					.attr("y", function(d) { return y(d[1])-5; })
					.attr("text-anchor", "middle");

				function mouseover(d){  // utility function to be called on mouseover.
					// // filter for selected state.
					// var st = fData.filter(function(s){ return s.l_month == d[0];})[0],
					// 	nD = d3.keys(st.leave).map(function(s){ return {type:s, leave:st.leave[s]};});

					// // call update functions of pie-chart and legend.
					// pC.update(nD);
					// leg.update(nD);
				}

				function mouseout(d){    // utility function to be called on mouseout.
					// // reset the pie-chart and legend.
					// pC.update(tF);
					// leg.update(tF);
				}

				// create function to update the bars. This will be used by pie-chart.
				hG.update = function(nD, color){
					// update the domain of the y-axis map to reflect change in frequencies.
					y.domain([0, d3.max(nD, function(d) { return d[1]; })]);

					// Attach the new data to the bars.
					var bars = hGsvg.selectAll(".bar").data(nD);

					// transition the height and color of rectangles.
					bars.select("rect").transition().duration(500)
						.attr("y", function(d) {return y(d[1]); })
						.attr("height", function(d) { return hGDim.h - y(d[1]); })
						.attr("fill", color);

					// transition the frequency labels location and change value.
					bars.select("text").transition().duration(500)
						.text(function(d){ return d3.format(",")(d[1])})
						.attr("y", function(d) {return y(d[1])-5; });
				}
			return hG;

			}

			//function to handle pieChart
			function pieChart(pD){
				var pC ={},    pieDim ={w:250, h: 250};
				pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

				//console.log('creating svg for pieChart')
				var piesvg = d3.select(id)
				.append("svg")
					.attr("width", pieDim.w).attr("height", pieDim.h).append("g")
					.attr("transform", "translate("+pieDim.w/2+","+pieDim.h/2+")");

				// create function to draw the arcs of the pie slices.
				var arc = d3.svg.arc()
					.outerRadius(pieDim.r - 70)
					.innerRadius(pieDim.r);

				//create a function to compute the pie slice angles.
				var pie = d3.layout.pie()
					.sort(null).value(function(d) {
						return d['amount'];
				});

				// Draw the pie slices.
				piesvg.selectAll("path")
				.data(pie(fstate))
				.enter().append("path").attr("d", arc)
					.each(function(d) { this._current = d['amount']; })
					.attr("fill", function(d, i){return color(i);});
					// .on("mouseover",mouseover).on("mouseout",mouseout)

				// create function to update pie-chart. This will be used by histogram.
				pC.update = function(nD){
					piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
						.attrTween("d", arcTween);
					}
				function mouseover(d, i){
					// call the update function of histogram with new data.
					//hG.update(fData.map(function(v){
					//return [v.l_month,v.leave[d.data.type]];}),color(i));
				}
				//Utility function to be called on mouseout a pie slice.
				function mouseout(d){
					// call the update function of histogram with all data.
					//hG.update(fData.map(function(v){
					//return [v.l_month,v.total];}), barColor);
				}
				function arcTween(a) {
					var i = d3.interpolate(this._current, a);
					this._current = i(0);
					return function(t) { return arc(i(t));    };
				}

				return pC;
			}

			//function to handle legend
			function legend(lD){
				var leg = {};

				//create table for legend
				var legend = d3.select(id).append("table").attr('class','legend');

				//create one row per segment.
				var tr = legend.append("tbody").selectAll("tr").data(fstate).enter().append("tr");

				// create the first column for each segment.
				tr.append("td").append("svg").attr("width", '20').attr("height", '20').append("rect")
				.attr("width", '16').attr("height", '16')
				.attr("fill",function(d, i){ return color(i) });

				//creating the second column for each segment'
				tr.append("td").text(function(d){ return d.state;});

				//creating the second column for each segment
				tr.append("td").text(function(d){ return d.amount;});

				leg.update = function(nD){
					// update the data attached to the row elements.
					var l = legend.select("tbody").selectAll("tr").data(nD);

					// update the frequencies.
					l.select(".legendFreq").text(function(d){ return d3.format(",")(d['amount']);});

					// update the percentage column.
					l.select(".legendPerc").text(function(d){ return getLegend(d,nD);});
				}

				return leg;
			}

			// calculate total frequency by segment for all state.
			var tF = fstate.map(function(d){
				return d['amount'], d['state'];
			});

			var sF = fData.map(function(d){
				return [fData.forEach(item => item[0]), fData.forEach(item => item[1])];
			});

			var hG = histoGram(sF), // create the histogram.
				pC = pieChart(tF), // create the pieChart
				leg = legend(tF); //create the legend

		});
	},


	render_department_expenditure: function(){
		var self = this;
		var w = 200;
		var h = 200;
		var r = h/2;
		var elem = this.$('.department_expenditure');

		var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
		'#ffa433', '#ffc25b', '#f8e54b'];
		var color = d3.scale.ordinal().range(colors);


		rpc.query({
			model: 'purchase.order',
			method: 'get_expenditure_by_department',

		}).then(function(data){
			var segColor = {};
			var vis = d3.select(elem[0]).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
			var pie = d3.layout.pie().value(function(d){return d.amount;});
			var arc = d3.svg.arc().outerRadius(r);
			var arcs = vis.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
			arcs.append("svg:path")
				.attr("fill", function(d, i){
					return color(i);
				})
				.attr("d", function (d) {
					return arc(d);
				});
			var legend = d3.select(elem[0]).append("table").attr('class','legend');
			// create one row per segment.
			var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");

			// create the first column for each segment.
			tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
				.attr("width", '16').attr("height", '16')
				.attr("fill",function(d, i){ return color(i) });

			// create the second column for each segment.
			tr.append("td").text(function(d){ return d.department;});

			// create the third column for each segment.
			tr.append("td").attr("class",'legendFreq')
				.text(function(d){ return d.amount;});
		});


	},


	render_purchase_analysis: function(){
		console.log('executing purchase trend analysis')
		var self = this;
		var w = 200;
		var h = 200;
		var r = h/2;
		var elem = this.$('.purchase_trends');

		var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
		'#ffa433', '#ffc25b', '#f8e54b'];
		var color = d3.scale.ordinal().range(colors);

		rpc.query({
			model: 'purchase.order',
			method: 'get_purchase_trend_analysis',

		}).then(function(data){
			var segColor = {};
			var vis =  d3.select(elem[0]).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
			var pie = d3.layout.pie().value(function(d){return d.value;});
			var arc = d3.svg.arc().outerRadius(r);
			var arcs = vis.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
			arcs.append("svg:path")
				.attr("fill", function(d, i){
					return color(i);
				})
				.attr("d", function (d) {
					return arc(d);
				});
			var legend = d3.select(elem[0]).append("table").attr('class','legend');

			// create one row per segment.
			var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");

			// create the first column for each segment.
			tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
				.attr("width", '16').attr("height", '16')
				.attr("fill",function(d, i){ return color(i) });

			// create the second column for each segment.
			tr.append("td").text(function(d){ return d.label;});

			// create the third column for each segment.
			tr.append("td").attr("class",'legendFreq')
				.text(function(d){ return d.value;});
		});
	},

	render_contract_trends: function(){
		var self = this;
		var w = 300;
		var h = 300;
		var r = h/2;
		var elem = this.$('.contracts_graph');

		var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
		'#ffa433', '#ffc25b', '#f8e54b'];
		var color = d3.scale.ordinal().range(colors);

		rpc.query({
			model: 'kola.contract',
			method: 'get_contracts_analysis',

		}).then(function(data){
			var segColor = {};

			var vis =  d3
				.select(elem[0])
				.append("svg:svg")
				.data([data])
				.attr("width", w)
				.attr("height", h)
				.append("svg:g")
				.attr("transform", "translate(" + r + "," + r + ")");

			var pie = d3.layout
				.pie()
				.value(function(d){
					return d.value;
				});

			var arc = d3.svg.arc()
				.outerRadius(r)
				.innerRadius(r-100);

			var arcs = vis.selectAll("g.slice")
				.data(pie).enter()
				.append("svg:g")
				.attr("class", "slice")
				.attr("stroke", "white")
				.style("stroke-width", "2px")
				.style("opacity", 0.7);

			arcs.append("svg:path")
				.attr("fill", function(d, i){
					return color(i);
				})
				.attr("d", function (d) {
					return arc(d);
				});

			arcs.append("text")
				.append("transform", function(d){
					return "translate("+label.centroid(d)+")";
				})
				.text(function(d){
					return d.label
				})

			// var legend = d3.select(elem[0]).append("table").attr('class','legend');

			// // create one row per segment.
			// var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");

			// // create the first column for each segment.
			// tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
			// 	.attr("width", '16').attr("height", '10')
			// 	.attr("fill",function(d, i){ return color(i) });

			// // create the second column for each segment.
			// tr.append("td").text(function(d){ return d.label;});

			// // create the third column for each segment.
			// tr.append("td").attr("class",'legendFreq')
			// 	.text(function(d){ return d.value;});
		});
	},

	reload: function () {
		return this.parent.load(['P2PDashboardInventory']);
	}

});



core.action_registry.add('procure2paysettings.main', Procure2PayDashboardMain);

return {
	Procure2PayDashboardMain: Procure2PayDashboardMain
	};

});
