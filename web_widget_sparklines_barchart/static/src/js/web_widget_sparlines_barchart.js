odoo.define('web_widget_sparklines_barchart', function (require) {
"use strict";

    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');

    var SparklinesChartWidget = AbstractField.extend({
        supportedFieldTypes: ['char'],
        jsLibs: ['/web_widget_sparklines_barchart/static/src/lib/jquery.sparkline.js'],
        start: function() {
            var type = 'bar'
            if (this.attrs.options && this.attrs.options.type){
                type = this.attrs.options.type
            }
            var barchart = $('<span>'+ [this.value] +'</span>');
            barchart.sparkline('html', {type: type, height: '20px',
                                        tooltipContainer: $(this.$el),
                                        tooltipClassname: 'sparktooltip'});
            this.$el.append(barchart);
            return this._super.apply(this, arguments);
        },
        _render: function () {
            $.sparkline_display_force_visible();
        },
    });

    fieldRegistry.add('sparklines_chart', SparklinesChartWidget);

    return {
        SparklinesChartWidget: SparklinesChartWidget
    };

});
