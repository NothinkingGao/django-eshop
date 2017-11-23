function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

	var _util = __webpack_require__(2);

	var _util2 = _interopRequireDefault(_util);

	var _dialog = __webpack_require__(1);

	var _dialog2 = _interopRequireDefault(_dialog);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	function alert() {
	    var content = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : '';
	    var yes = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : _util2.default.noop;
	    var options = arguments[2];

	    if ((typeof yes === 'undefined' ? 'undefined' : _typeof(yes)) === 'object') {
	        options = yes;
	        yes = _util2.default.noop;
	    }

	    options = _util2.default.extend({
	        content: content,
	        buttons: [{
	            label: '确定',
	            type: 'primary',
	            onClick: yes
	        }]
	    }, options);

	    return (0, _dialog2.default)(options);
	}
	exports.default = alert;
	module.exports = exports['default'];

/***/ },