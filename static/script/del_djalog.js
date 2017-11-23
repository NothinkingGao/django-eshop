function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _util = __webpack_require__(2);

	var _util2 = _interopRequireDefault(_util);

	var _dialog = __webpack_require__(6);

	var _dialog2 = _interopRequireDefault(_dialog);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var _sington = void 0;

	function dialog() {
	    var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

	    if (_sington) return _sington;

	    var isAndroid = _util2.default.os.android;
	    options = _util2.default.extend({
	        title: null,
	        content: '',
	        className: '',
	        buttons: [{
	            label: '确定',
	            type: 'primary',
	            onClick: _util2.default.noop
	        }],
	        isAndroid: isAndroid
	    }, options);

	    var $dialogWrap = (0, _util2.default)(_util2.default.render(_dialog2.default, options));
	    var $dialog = $dialogWrap.find('.weui-dialog');
	    var $mask = $dialogWrap.find('.weui-mask');

	    function _hide(callback) {
	        _hide = _util2.default.noop; // 防止二次调用导致报错

	        $mask.addClass('weui-animate-fade-out');
	        $dialog.addClass('weui-animate-fade-out').on('animationend webkitAnimationEnd', function () {
	            $dialogWrap.remove();
	            _sington = false;
	            callback && callback();
	        });
	    }
	    function hide(callback) {
	        _hide(callback);
	    }

	    (0, _util2.default)('body').append($dialogWrap);
	    // 不能直接把.weui-animate-fade-in加到$dialog，会导致mask的z-index有问题
	    $mask.addClass('weui-animate-fade-in');
	    $dialog.addClass('weui-animate-fade-in');

	    $dialogWrap.on('click', '.weui-dialog__btn', function (evt) {
	        var index = (0, _util2.default)(this).index();
	        if (options.buttons[index].onClick) {
	            if (options.buttons[index].onClick.call(this, evt) !== false) hide();
	        } else {
	            hide();
	        }
	    });

	    _sington = $dialogWrap[0];
	    _sington.hide = hide;
	    return _sington;
	}
	exports.default = dialog;
	module.exports = exports['default'];

/***/ },