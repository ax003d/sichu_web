var on_check_isbn = function() {
	var $isbn = $("#form_add_book #isbn");
	var ret = false;

	if(!cabinet.check_length($isbn, 10, 13)) {
		$("#isbn_err").text("ISBN错误!").show();
		return ret;
	}

	$.ajax({
		url : '/cabinet/check_isbn/?isbn=' + $isbn.val(),
		async : false,
		success : function(data) {
			if(data == "无法找到该书!") {
				$("#isbn_err").text("未搜索到该书!").show();
				return;
			}

			$("#form_add_book .chkBookInfo").html(data);
			ret = true;
		}
	});
	return ret;
};
// btn_check

var form_add_book = function() {
	$("#form_add_book").submit(function(event) {
		event.preventDefault();
		var $isbn = $("#form_add_book #isbn");
		if(!cabinet.check_length($isbn, 10, 13)) {
			alert("请输入ISBN!(10 ~ 13位数字)");
			return;
		}

		if ( $("#form_add_book #remark").val() == "填写备注" ) {
			$("#form_add_book #remark").val("");
		}
		var vals = $(this).serialize();
		// console.log(vals);
		$.post("/cabinet/add_book/", vals, function(json) {
			if(json['success'] == true) {
				$isbn.val("");
				$("#form_add_book #remark").val("");
				$(".step3").hide();
				$(".step4").show();
			} else {
				alert("添加书籍失败!");
			}
		});
	});
};
// form_add_book

$(document).ready(function() {
	$(".go_step_1").click(function(event) {
		event.preventDefault();
		$(".step2, .step3, .step4").hide();
		$(".step1").show();
	});

	$(".go_step_2").click(function(event) {
		event.preventDefault();
		$(".step1, .step3, .step4").hide();
		$(".step2").show();
	});

	$(".go_step_3").click(function(event) {
		event.preventDefault();
		$(".step1, .step2, .step4").hide();
		$(".step3").show();
	});

	$("#btn_chk_isbn").click(function(event) {
		event.preventDefault();
		if(on_check_isbn()) {
			$(".step1, .step3").hide();
			$(".step2").show();
		}
	});
	form_add_book();
	$(".btn_finish").click(function(event) {
		// console.log("finish");
		$("#form_add_book").submit();
	});

	$(".radio-set").buttonset();

	var isbn_tips = "请输入书籍ISBN";
	$("#form_add_book #isbn").focus(function() {
		// console.debug("focus");
		if($(this).val() == isbn_tips) {
			$(this).val("");
		}
	}).blur(function() {
		if($(this).val() == "") {
			$(this).val(isbn_tips);
		}
	});
	var remark_tips = "填写备注";
	$("#form_add_book #remark").focus(function() {
		// console.debug("focus");
		if($(this).val() == remark_tips) {
			$(this).val("");
		}
	}).blur(function() {
		if($(this).val() == "") {
			$(this).val(remark_tips);
		}
	});
});
