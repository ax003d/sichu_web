var cabinet = {};
cabinet.page_num = {};

cabinet.check_length = function(o, min, max) {
	if (o.val().length > max || o.val().length < min) {
		o.addClass("ui-state-error");
		return false;
	} else {
		return true;
	}
};
// check_length

cabinet.check_regexp = function(o, regexp) {
	if (!(regexp.test(o.val()) )) {
		o.addClass("ui-state-error");
		return false;
	} else {
		return true;
	}
};
// check_regexp

cabinet.check_email = function(o) {
	return cabinet.check_regexp(o, /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
};
// check_email

cabinet.show_dialog = function(dlg) {
	$("#overlay").height($(document).height());
	if (dlg.parent()[0] != $("body")[0]) {
		dlg.appendTo($("body"));
	}
	dlg.css("top", $(document).scrollTop() + Math.abs($(window).height() - dlg.height()) / 2 + "px");
	// console.log($(document).scrollTop() + Math.abs($(window).height() - dlg.height()) / 2 + "px");
	$("#overlay").show();
	dlg.show();
};
// show_dialog

cabinet.close_dialog = function(dlg) {
	$("#overlay").hide();
	dlg.hide();
}
var on_tab_item_clicked = function(event) {
	event.preventDefault();
	var tab_id = this.href.split('#')[1];
	$tab = $(this).parent().parent();
	$tab.children("li").removeClass("cabinet-tab-selected");
	$(this).parent().addClass("cabinet-tab-selected");
	$tab.parent().children("div").hide();
	$tab.parent().children("." + tab_id).show();
};
// on_tab_item_clicked

cabinet.get_wnd_idx = function(lst_len, wnd_len, idx) {
	// console.debug(lst_len, wnd_len, idx);
	if (idx < 1) {
		idx = 1;
	}
	if (idx > lst_len) {
		idx = lst_len;
	}

	if (lst_len <= wnd_len) {
		return Array(1, lst_len, idx);
	}

	var hd_intvl = Math.floor(wnd_len / 2);
	var tl_intvl = wnd_len - hd_intvl - 1;
	var wnd_idx = hd_intvl + 1;

	var hd_idx = idx - hd_intvl;
	var tl_idx = idx + tl_intvl;
	var delta = 0;
	if (hd_idx < 1) {
		delta = 1 - hd_idx;
		hd_idx = 1;
		tl_idx += delta;
		wnd_idx -= delta;
	}
	if (tl_idx > lst_len) {
		delta = tl_idx - lst_len;
		hd_idx -= delta;
		tl_idx = lst_len;
		wnd_idx += delta;
	}

	return Array(hd_idx, tl_idx, wnd_idx);
};
// get_wnd_idx

var test_get_wnd_idx = function() {
	var lst_len = 5;
	var wnd_len = 9;
	// [1, 5, 3]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 3));
	// [1, 5, 5]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 20));
	// [1, 5, 1]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, -1));
	lst_len = 9;
	// [1, 9, 3]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 3));
	// [1, 9, 9]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 20));
	// [1, 9, 1]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, -1));
	lst_len = 50;
	// [1, 9, 3]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 3));
	// [16, 24 ,5]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 20));
	// [41, 50, 7]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, 48));
	// [1, 9, 1]
	// console.debug(cabinet.get_wnd_idx(lst_len, wnd_len, -1));
};
// test_get_wnd_idx

cabinet.go_page = function(type, page) {
	// console.debug("go_page", type);
	if (page < 1) {
		page = 1;
	}
	if (page > cabinet.page_num[type]) {
		page = cabinet.page_num[type];
	}

	var cur_page_id = "#page-" + cabinet.cur_type + "-" + cabinet.cur_page;
	var nxt_page_id = "#page-" + type + "-" + page;
	var $input_page = $(".input_page");

	if ($(nxt_page_id).length != 0) {
		$(cur_page_id).hide();
		$(nxt_page_id).show();
		cabinet.cur_type = type;
		cabinet.cur_page = page;
		$input_page.val(page);
		cabinet.mark_page(type);
		return;
	}

	$.ajax({
		url : '/cabinet/books/' + type + '/' + page + '/',
		async : false,
		success : function(data) {
			$(cur_page_id).hide();
			var get_page_id = $(data)[0].id;
			$("#" + get_page_id).remove();
			$("#" + type + "-book-page").append(data);

			var lst = get_page_id.split('-');
			cabinet.cur_type = lst[1];
			cabinet.cur_page = parseInt(lst[2]);
			$input_page.val(cabinet.cur_page);
			cabinet.mark_page(type);
		}
	});
};
// go_page

cabinet.mark_page = function(type) {
	var ret = cabinet.get_wnd_idx(cabinet.page_num[type], 8, cabinet.cur_page);
	// console.debug(type, ret);
	$(".page-nav:visible").each(function() {
		$(this).find(".btn_page").each(function(index) {
			var start = ret[0];
			var end = ret[1];
			var idx = ret[2];

			this.id = "";
			$(this).show();
			$(this).text(start + index);
			if (index == idx - 1) {
				this.id = "page-selected";
			}
			if (start + index > end) {
				$(this).hide();
			}
		});
	});
};
// mark_page

$(document).ready(function() {
	$(".cabinetTabItem").click(on_tab_item_clicked);

	$(".btn_1st_page").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, 1);
	});
	$(".btn_prev_page").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, Math.abs(cabinet.cur_page - 1));
	});
	$(".btn_nxt_page").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, Math.abs(cabinet.cur_page + 1));
	});
	$(".btn_last_page").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, cabinet.page_num[cabinet.cur_type]);
	});
	$(".btn_page").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, parseInt($(this).text()));
	});
	$("#go_page_dw").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, parseInt($("#input_page_dw").val()));
	});
	$("#go_page_up").click(function(event) {
		event.preventDefault();
		cabinet.go_page(cabinet.cur_type, parseInt($("#input_page_up").val()));
	});
});
