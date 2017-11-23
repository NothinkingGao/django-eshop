function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _util = __webpack_require__(2);

	var _util2 = _interopRequireDefault(_util);

	var _topTips = __webpack_require__(16);

	var _topTips2 = _interopRequireDefault(_topTips);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var _toptips = null;

	function topTips(content) {
	    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

	    if (typeof options === 'number') {
	        options = {
	            duration: options
	        };
	    }

	    if (typeof options === 'function') {
	        options = {
	            callback: options
	        };
	    }

	    options = _util2.default.extend({
	        content: content,
	        duration: 3000,
	        callback: _util2.default.noop,
	        className: ''
	    }, options);

	    var $topTips = (0, _util2.default)(_util2.default.render(_topTips2.default, options));
	    function _hide(callback) {
	        _hide = _util2.default.noop; // 防止二次调用导致报错

	        $topTips.remove();
	        callback && callback();
	        options.callback();
	        _toptips = null;
	    }
	    function hide(callback) {
	        _hide(callback);
	    }

	    (0, _util2.default)('body').append($topTips);
	    if (_toptips) {
	        clearTimeout(_toptips.timeout);
	        _toptips.hide();
	    }

	    _toptips = {
	        hide: hide
	    };
	    _toptips.timeout = setTimeout(hide, options.duration);

	    $topTips[0].hide = hide;
	    return $topTips[0];
	}
	exports.default = topTips;
	module.exports = exports['default'];

},