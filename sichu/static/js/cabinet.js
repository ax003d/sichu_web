var cabinet = {}

cabinet.update_tips = function(tips, txt) {
	tips.text(txt).addClass("ui-state-highlight");
	setTimeout(function() {
		tips.removeClass("ui-state-highlight", 1500);
	}, 500);
};
// update_tips

cabinet.check_length = function(o, min, max) {
	if(o.val().length > max || o.val().length < min) {
		o.addClass("ui-state-error");
		return false;
	} else {
		return true;
	}
};
// check_length

cabinet.check_regexp = function(o, regexp) {
	if(!(regexp.test(o.val()) )) {
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

cabinet.form_chg_pwd = function() {
	$("#form_chg_pwd").submit(function(event) {
		event.preventDefault();
		$("#form_chg_pwd #old_pwd, #password1, #password2").removeClass("ui-state-error");
		var $tips = $("#tabs-chg-pwd .validate-tips");
		var $password1 = $("#form_chg_pwd #password1");
		var $password2 = $("#form_chg_pwd #password2");

		if(!cabinet.check_length($password1, 6, 8)) {
			cabinet.update_tips($tips, "密码应为 6 ~ 8 个字符!");
			return;
		}
		if($password1.val() != $password2.val()) {
			cabinet.update_tips($tips, "两次输入的密码不一致!");
			$password1.addClass("ui-state-error");
			$password2.addClass("ui-state-error");
			return;
		}
		var vals = $(this).serialize();
		$.post("/cabinet/chg_pwd/", vals, function(json) {
			if(json['success'] == true) {
				cabinet.update_tips($tips, "密码修改成功!");
				$("#form_chg_pwd #old_pwd").val("");
				$password1.val("");
				$password2.val("");
			} else if(json['old_pwd_err']) {
				cabinet.update_tips($tips, "旧密码错误!");
				$("#form_chg_pwd #old_pwd").addClass("ui-state-error");
			} else if(json['new_pwd_err']) {
				cabinet.update_tips($tips, "两次输入的密码不一致!");
				$("#form_chg_pwd #password1").addClass("ui-state-error");
				$("#form_chg_pwd #password2").addClass("ui-state-error");
			}
		});
	});
};
// form_chg_pwd

cabinet.form_chg_personal_info = function() {
	$("#form_chg_personal_info").submit(function(event) {
		event.preventDefault();

		var $last_name = $("#form_chg_personal_info #last_name");
		var $first_name = $("#form_chg_personal_info #first_name");
		var $email = $("#form_chg_personal_info #email");
		var $tips = $("#tabs-personal-info .validate-tips");

		$last_name.removeClass("ui-state-error");
		$first_name.removeClass("ui-state-error");
		$email.removeClass("ui-state-error");

		if(!cabinet.check_length($last_name, 1, 6)) {
			cabinet.update_tips($tips, "请输入姓氏!(1 ~ 6  个字符)");
			return;
		}
		if(!cabinet.check_length($first_name, 1, 6)) {
			cabinet.update_tips($tips, "请输入名字!(1 ~ 6 个字符)");
			return;
		}
		if(!cabinet.check_email($email)) {
			cabinet.update_tips($tips, "请输入正确的 email 地址!");
			return;
		}

		var vals = $(this).serialize();
		$.post("/cabinet/chg_personal_info/", vals, function(json) {
			if(json['email_used'] == true) {
				cabinet.update_tips($tips, "该电子邮件已经被使用!");
				email.addClass("ui-state-error");
			} else if(json['success'] == true) {
				cabinet.update_tips($tips, "成功保存个人信息!");
			}
		});
	});
};
// form_chg_personal_info

cabinet.form_add_book = function() {
	$("#form_add_book").submit(function(event) {
		event.preventDefault();

		var $isbn = $("#form_add_book #isbn");
		var $tips = $(".content-add-book .validate-tips");

		$isbn.removeClass("ui-state-error");

		if(!cabinet.check_length($isbn, 10, 13)) {
			cabinet.update_tips($tips, "请输入ISBN!(10 ~ 13位数字)");
			return;
		}

		var vals = $(this).serialize();
		$.post("/cabinet/add_book/", vals, function(json) {
			if(json['success'] == true) {
				cabinet.update_tips($tips, "成功添加书籍!");
				console.debug("success");
			} else {
				cabinet.update_tips($tips, json['message']);
			}
		});
	});
};
// form_add_book

cabinet.form_edit_bookownership = function() {
	$("#form_edit_bookownership").submit(function(event) {
		event.preventDefault();
		var vals = $(this).serialize();
		var $tips = $("#form_edit_bookownership .validate-tips");
		$.post("/cabinet/edit_bookownership/", vals, function(json) {
			if(json['success'] == true) {
				cabinet.update_tips($tips, "成功修改书籍信息!");
			} else {
				cabinet.update_tips($tips, "修改书籍信息失败!");
			}
		});
	});
};
// form_edit_bookownership

cabinet.form_ebook_request = function() {
	$("#form_ebook_request").submit(function(event) {
		event.preventDefault();
		var $tips = $(".book-request .validate-tips");
		var vals = $(this).serialize();
		$.post("/cabinet/ebook_request/", vals, function(json) {
			$tips.show();
			if(json['success'] == true) {
				cabinet.update_tips($tips, "成功发送索取电子版请求!")
			} else {
				cabinet.update_tips($tips, "发送索取电子版请求失败!")
			}
		});
	});
};
// form_ebook_request

cabinet.form_borrow_accept = function() {
	$("#form_borrow_accept").submit(function(event) {
		event.preventDefault();
		var $tips = $("#form_borrow_accept .validate-tips");
		var vals = $(this).serialize();
		$.post("/cabinet/borrow_accept/", vals, function(json) {
			if(json['success'] == true) {
				cabinet.show_sys_msgs();
			} else {
				$tips.show();
				cabinet.update_tips($tips, json['message'])
			}
		});
	});
};
// form_borrow_accept

cabinet.form_return_book = function() {
	$("#form_return_book").submit(function(event) {
		event.preventDefault();
		var $tips = $("#form_return_book .validate-tips");
		var vals = $(this).serialize();
		$.post("/cabinet/return_book/", vals, function(json) {
			if(json['success'] == true) {
				cabinet.show_loaned_books();
			} else {
				$tips.show();
				cabinet.update_tips($tips, "归还书籍失败!")
			}
		});
	});
};
// form_return_book

cabinet.form_del_ebook_request = function() {
	$("#form_del_ebook_request").submit(function(event) {
		event.preventDefault();
		var $tips = $("#form_del_ebook_request .validate-tips");
		var vals = $(this).serialize();
		$.post("/cabinet/del_ebook_request/", vals, function(json) {
			if(json['success'] == true) {
				cabinet.show_sys_msgs();
			} else {
				$tips.show();
				cabinet.update_tips($tips, "删除请求失败!")
			}
		});
		window.location.hash = "tabs-ebook-request";
	});
};
// form_del_ebook_request

cabinet.form_search = function() {
	$("#form_search").submit(function(event) {
		event.preventDefault();
		var vals = $(this).serialize();
		$.post("/cabinet/search/", vals, function(data) {
			$(".ui-layout-center").html(data);
		});
	});
};
// form_search

cabinet.form_create_repo = function() {
	$("#form_create_repo").submit(function(event) {
		event.preventDefault();
		var $tips = $("#form_create_repo .validate-tips");
		var $name = $("#form_create_repo #name");
		var $desc = $("#form_create_repo #description");

		$tips.hide();
		$name.removeClass("ui-state-error");
		$desc.removeClass("ui-state-error");

		if(!cabinet.check_length($name, 3, 16)) {
			$tips.show();
			cabinet.update_tips($tips, "馆名为3~16个字符!");
			$name.addClass("ui-state-error");
			return false;
		}
		if(!cabinet.check_length($desc, 5, 256)) {
			$tips.show();
			cabinet.update_tips($tips, "请输入公馆说明，至少5个字符!")
			$desc.addClass("ui-state-error");
			return false;
		}

		var vals = $(this).serialize();
		$.post("/cabinet/create_repo/", vals, function(json) {
			if(json['success'] == true) {
				$("#dlg_create_repo").dialog("close");
				$name.val("");
				$desc.val("");
				cabinet.show_repos();
			} else {
				$tips.show();
				cabinet.update_tips($tips, json['message']);
			}
		});
	});
};
// form_create_repo

cabinet.form_repo_apply = function() {
	$("#form_repo_apply").submit(function(event) {
		event.preventDefault();
		var $tips = $("#form_repo_apply .validate-tips");
		$tips.hide();
		var vals = $(this).serialize();
		$.post("/cabinet/repo_apply/", vals, function(json) {
			if(json['success'] == true) {
				$("#dlg_repo_apply").dialog("close");
				$("#form_repo_apply #remark").val("");
				cabinet.show_other_repos();
			} else {
				$tips.show();
				cabinet.update_tips($tips, json['message']);
			}
		});
	});
};
// form_repo_apply

cabinet.form_join_repo_process = function() {
	$("#form_join_repo_process").submit(function(event) {
		event.preventDefault();
		var $tips = $("#form_join_repo_process .validate-tips");
		$tips.hide();
		var vals = $(this).serialize();
		$.post("/cabinet/join_repo_process/", vals, function(json) {			
			if(json['success'] == true) {
				cabinet.show_sys_msgs();
			} else {				
				$tips.show();
				cabinet.update_tips($tips, json['message']);
			}
		});
	});
};
// form_join_repo_process

cabinet.show_sys_msgs = function() {
	$(".ui-layout-center").load('/cabinet/sys_msgs/', function() {
		$(".sys-msg").tabs();
		cabinet.form_borrow_accept();
		cabinet.form_del_ebook_request();
		cabinet.form_join_repo_process();
	});
};
// show_sys_msgs

cabinet.on_send_test_mail = function() {
	var $email = $("#form_chg_personal_info #email");
	var $tips = $("#tabs-personal-info .validate-tips");
	if(!cabinet.check_email($email)) {
		cabinet.update_tips($tips, "请输入正确的 email 地址!");
		return;
	}
	$.get("/cabinet/send_test_mail/", {
		'email' : $email.val()
	}, function(json) {
		if(json['success'] == true)
			cabinet.update_tips($tips, "成功发送测试邮件, 请注意查收!");
	});
};
// on_send_test_mail

cabinet.show_personal_info = function() {
	$(".ui-layout-center").load('/cabinet/personal_infos/', function() {
		$(".personal-infos").tabs();
		$("input:submit, .button").button();
		cabinet.form_chg_pwd();
		cabinet.form_chg_personal_info();
	});
};
// show_personal_info

cabinet.show_add_book = function() {
	$(".ui-layout-center").load('/cabinet/add_book/', function() {
		$("input:submit").button();
		cabinet.form_add_book();
	});
};
// show_add_book

cabinet.show_all_books = function() {
	$(".ui-layout-center").load("/cabinet/all_books/");
};
// show_all_books

cabinet.show_loaned_books = function() {
	$(".ui-layout-center").load("/cabinet/loaned_books/", function() {
		cabinet.form_return_book();
	});
};
// show_loaned_books

cabinet.show_borrowed_books = function() {
	$(".ui-layout-center").load("/cabinet/borrowed_books/");
};
// show_borrowed_books

cabinet.show_userinfo = function(event, href) {
	event.preventDefault();
	$(".ui-layout-center").load(href);
};
// show_userinfo

cabinet.show_bookinfo = function(event, href) {
	event.preventDefault();
	$(".ui-layout-center").load(href);
};
// show_bookinfo

cabinet.show_repoinfo = function(event, href) {
	event.preventDefault();
	$(".ui-layout-center").load(href, function() {
		$(".repo-tabs").tabs();
	});
};
// show_repoinfo

cabinet.show_news = function() {
	$(".ui-layout-center").load('/cabinet/show_news/');
};
// show_news

cabinet.show_bookownershipinfo = function(event, href) {
	event.preventDefault();
	$(".ui-layout-center").load(href, function() {
		cabinet.form_edit_bookownership();
		cabinet.form_ebook_request();
		$("#btn_request_ebook").click(function() {
			$("#form_ebook_request").submit();
		});
	});
};
// show_bookownershipinfo

cabinet.show_search = function() {
	$(".ui-layout-center").load("/cabinet/search/", function() {
		cabinet.form_search();
	});
};
// show_search

cabinet.show_about = function() {
	$(".ui-layout-center").load("/cabinet/about/");
};
// show_about

cabinet.show_repos = function() {
	$(".ui-layout-center").load("/cabinet/repos/");
};
// show_repos

cabinet.show_other_repos = function() {
	$(".ui-layout-center").load("/cabinet/other_repos/");
};
// show_other_repos

cabinet.create_dlg_borrow_request = function() {
	$("#dlg_borrow_request").dialog({
		autoOpen : false,
		modal : true
	});
	$(".date-picker").datepicker({
		"dateFormat" : "yy-mm-dd"
	});
	$("#form_borrow_request").submit(function(event) {
		event.preventDefault();

		var $planed_dt = $("#form_borrow_request #planed_return_date");
		var $tips = $("#form_borrow_request .validate-tips");

		// $planed_dt.removeClass("ui-state-error");
		// var dt = new Date();
		// to-do: not supported in IE6, 7, 8, find some methods to do this thing. js string lib?
		// if ( dt.toISOString() > $planed_dt.val() ) {
		// $planed_dt.addClass("ui-state-error");
		// $tips.show();
		// cabinet.update_tips($tips, "归还日期不能早于当天!");
		// return false;
		// }

		var vals = $(this).serialize();
		$.post("/cabinet/borrow_request/", vals, function(json) {
			$tips.show();
			if(json['success'] == true) {
				cabinet.update_tips($tips, "成功发送借阅请求!");
			} else {
				cabinet.update_tips($tips, json['message']);
			}
		});
	});
};
// create_dlg_borrow_request

cabinet.create_dlg_create_repo = function() {
	$("#dlg_create_repo").dialog({
		autoOpen : false,
		modal : true
	});
	cabinet.form_create_repo();
};
// create_dlg_create_repo

cabinet.create_dlg_repo_apply = function() {
	$("#dlg_repo_apply").dialog({
		autoOpen : false,
		modal : true
	});
	cabinet.form_repo_apply();
};
// create_dlg_repo_apply

cabinet.prepare_dlg = function(dlg_type) {
	var create_dict = {
		"dlg_borrow_request" : cabinet.create_dlg_borrow_request,
		"dlg_create_repo" : cabinet.create_dlg_create_repo,
		"dlg_repo_apply" : cabinet.create_dlg_repo_apply
	}
	var query = "[aria-labelledby=ui-dialog-title-" + dlg_type + "]";
	if($(query).length != 0)
		return;

	$.ajax({
		url : "/cabinet/get_dlg/",
		data : {
			"dlg_type" : dlg_type
		},
		async : false,
		success : function(data) {
			$("#inner-body").append(data);
			$("input:submit").button();
			create_dict[dlg_type]();
		}
	});
}
// prepare_dlg

cabinet.show_cabinet = function(event, href) {
	event.preventDefault();
	$(".ui-layout-center").load(href, function() {
		$(".bookownershipinfo").click(function(event) {
			cabinet.show_bookownershipinfo(event, this.href);
		});
	});
};
// show_cabinet

cabinet.on_borrow_accept = function(brid) {
	$("#form_borrow_accept #brid").val(brid);
	$("#form_borrow_accept #accepted").val(1);
	$("#form_borrow_accept").submit();
};
// on_borrow_accept

cabinet.on_borrow_denied = function(brid) {
	$("#form_borrow_accept #brid").val(brid);
	$("#form_borrow_accept #accepted").val(0);
	$("#form_borrow_accept").submit();
};
// on_borrow_denied

cabinet.on_book_returned = function(brid) {
	$("#form_return_book #br_id").val(brid);
	$("#form_return_book #br_id").submit();
};
// on_book_returned

cabinet.on_del_ebook_request = function(eqid) {
	$("#form_del_ebook_request #eqid").val(eqid);
	$("#form_del_ebook_request").submit();
};
// on_del_ebook_request

cabinet.on_borrow_request = function(boid) {
	cabinet.prepare_dlg("dlg_borrow_request");
	$("#form_borrow_request .validate-tips").hide();
	$("#form_borrow_request #boid").val(boid);
	$("#dlg_borrow_request").dialog("open");
};
// on_create_group

cabinet.on_create_repo = function() {
	cabinet.prepare_dlg("dlg_create_repo");
	$("#dlg_create_repo").dialog("open");
};
// on_create_repo

cabinet.on_repo_apply = function(repo_id) {
	cabinet.prepare_dlg("dlg_repo_apply");
	$("#form_repo_apply #repo_id").val(repo_id);
	$("#dlg_repo_apply").dialog("open");
};
// on_repo_apply

cabinet.on_join_repo_accepted = function(jr_id) {
	$("#form_join_repo_process #jr_id").val(jr_id);
	$("#form_join_repo_process #accepted").val(1);
	$("#form_join_repo_process").submit();
};
// on_join_repo_accepted

cabinet.on_join_repo_denied = function(jr_id) {
	$("#form_join_repo_process #jr_id").val(jr_id);
	$("#form_join_repo_process #accepted").val(0);
	$("#form_join_repo_process").submit();
};
// on_join_repo_denied
