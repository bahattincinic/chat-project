function autosize() {
	// auto adjust the height of
	$('body').on('keyup', 'textarea', function (){
		$(this).height(0);
		$(this).height(this.scrollHeight);
	});
	// $('body').find('textarea.comment-reply-textarea').keyup();
}
function showButton(id) {
	$('#comment_btn_'+id).fadeIn('slow');
}
function loadChat(uid, username, block, cid, start) {
	if(!cid) {
		$('.message-loader').show();
	} else {
		$('.load-more-chat').html('<div class="preloader-retina preloader-center"></div>');
	}
	$.ajax({
		type: "POST",
		url: "requests/load_chat.php",
		data: "uid="+uid+"&cid="+cid+"&start="+start, 
		cache: false,
		success: function(html) {
			// Remove the loader animation
			if(!cid) {
				$('.chat-container').empty();
				$('.message-loader').hide();
				$('#chat').attr('class', 'chat-user'+uid);
			} else {
				$('.load-more-chat').remove();
			}
			if(username) {
				$('.chat-username').html(username);
			}
			
			if(block) {
				doBlock(uid, 0);
			}
			
			// Append the new comment to the div id
			$('.chat-container').prepend(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
		}
	});
}
function loadComments(id, cid, start) {
	$('#more_comments_'+id).html('<div class="preloader-retina preloader-center"></div>');
	$.ajax({
		type: "POST",
		url: "requests/load_comments.php",
		data: "id="+id+"&start="+start+"&cid="+cid, 
		cache: false,
		success: function(html) {
			// Remove the loader animation
			$('#more_comments_'+id).remove();
			
			// Append the new comment to the div id
			$('#comments-list'+id).prepend(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
		}
	});
}
function loadTimeline(start, filter) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	if(filter == '') {
		q = '';
	} else {
		q = '&filter='+filter;
	}
	
	$.ajax({
		type: "POST",
		url: "requests/load_timeline.php",
		data: "start="+start+q, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
			
			autosize();
		}
	});
}
function loadFeed(start, filter) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	if(filter == '') {
		q = '';
	} else {
		q = '&filter='+filter;
	}
	
	$.ajax({
		type: "POST",
		url: "requests/load_feed.php",
		data: "start="+start+q, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
			
			autosize();
		}
	});
}
function loadPeople(start, value, filter) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	if(filter == '') {
		q = '';
	} else {
		q = '&filter='+filter;
	}
	
	$.ajax({
		type: "POST",
		url: "requests/load_people.php",
		data: "start="+start+'&q='+encodeURIComponent(value)+q, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
			
			autosize();
		}
	});
}
function loadProfile(start, filter, profile) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	if(filter == '') {
		q = '';
	} else {
		q = '&filter='+filter;
	}
	
	$.ajax({
		type: "POST",
		url: "requests/load_profile.php",
		data: "profile="+profile+"&start="+start+q, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
			
			autosize();
		}
	});
}
function loadHashtags(start, value) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	$.ajax({
		type: "POST",
		url: "requests/load_tags.php",
		data: "start="+start+'&q='+value, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
			
			autosize();
		}
	});
}
function loadLikes(start, id, profile) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	$.ajax({
		type: "POST",
		url: "requests/load_likes.php",
		data: "start="+start+'&profile='+profile, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		
			// Reload the timeago plugin
			jQuery("span.timeago").timeago();
			
			autosize();
		}
	});
}
function loadSubs(start, type, profile) {
	$('#more_messages').html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	$.ajax({
		type: "POST",
		url: "requests/load_subs.php",
		data: "id="+profile+"&start="+start+"&type="+type, 
		cache: false,
		success: function(html) {
			$('#more_messages').remove();
			
			// Append the new comment to the div id
			$('#messages').append(html);
		}
	});
}
function postComment(id) {
	var comment = $('#comment-form'+id).val();
	
	$('#post_comment_'+id).html('<div class="preloader-retina-large preloader-center"></div>');
	
	// Remove the post button
	$('#comment_btn_'+id).fadeOut('slow');
	
	$.ajax({
		type: "POST",
		url: "requests/post_comment.php",
		data: "id="+id+"&comment="+encodeURIComponent(comment), 
		cache: false,
		success: function(html) {
			// Remove the loader animation
			$('#post_comment_'+id).html('');
			
			// Append the new comment to the div id
			$('#comments-list'+id).append(html);
			
			// Fade In the style="display: none" class
			$('.message-reply-container').fadeIn(500);
			
			// Reload the timeago plugin
			jQuery("div.timeago").timeago();
			
			// Empty the text area
			$('#comment-form'+id).val('');
		}
	});
}
function share(id) {
	$('#share').show('slow');
	
	$('.share-close').hide();
	$('.share-btn').show();
	$('.share-cancel').show();
	
	$('.share-btn').attr('onclick', 'doShare('+id+', 1)');
	$('.share-cancel').attr('onclick', 'doShare(0, 0)');
}
function doShare(id, type) {
	if(type) {
		$('.share-btn').hide();
		$('.share-cancel').hide();
		$('.share-close').show();
		$('.share-desc').html('<div class="preloader-retina-large preloader-center"></div>');
		
		$.ajax({
			type: "POST",
			url: "requests/share.php",
			data: "id="+id, 
			cache: false,
			success: function(html) {
				$('.share-desc').html(html);
			}
		});
	} else {
		$('#share').hide('slow');
	}
}
function delete_the(id, type) {
	// id = unique id of the message/comment/chat
	// type = type of post: message/comment/chat
	if(type == 0) {
		$('#del_comment_'+id).html('<div class="preloader-retina"></div>');
	} else if(type == 1) {
		$('#del_message_'+id).html('<div class="preloader-retina-large preloader-center"></div>');
	} else if(type == 2) {
		$('#del_chat_'+id).html('<div class="preloader-retina"></div>');
	}
	
	$.ajax({
		type: "POST",
		url: "requests/delete.php",
		data: "message="+id+"&type="+type, 
		cache: false,
		success: function(html) {
			if(html == '1') {
				if(type == 0) {
					$('#comment'+id).fadeOut(500, function() { $('#comment'+id).remove(); });
				} else if(type == 1) {
					$('#message'+id).fadeOut(500, function() { $('#message'+id).remove(); });
				} else if(type == 2) {
					$('#chat'+id).fadeOut(500, function() { $('#chat'+id).remove(); });
				}
			} else {
				if(type == 0) {
					$('#comment'+id).html($('#del_comment_'+id).html('Sorry, the comment could not be removed, please refresh the page and try again.'));
				} else if(type == 1) {
					$('#message'+id).html($('#del_message_'+id).html('<div class="message-content"><div class="message-inner">Sorry, the message could not be removed, please refresh the page and try again.</div></div>'));
				} else if(type == 2) {
					$('#chat'+id).html($('#del_chat_'+id).html('Sorry, the chat message could not be removed, please refresh the page and try again.'));
				}
			}
		}
	});
}
function report_the(id, type) {
	// id = unique id of the message/comment
	// type = type of post: message/comment
	
	if(type == 0) {
		$('#comment'+id).html('<div class="message-reported"><div class="preloader-retina"></div></div>');
	} if(type == 1) {
		$('#message'+id).html('<div class="message-reported"><div class="preloader-retina-large preloader-center"></div></div>');
	}
	
	$.ajax({
		type: "POST",
		url: "requests/report.php",
		data: "id="+id+"&type="+type, 
		cache: false,
		success: function(html) {
			if(type == 0) {
				$('#comment'+id).html('<div class="message-reported">'+html+'</div>');
			} if(type == 1) {
				$('#message'+id).html('<div class="message-content"><div class="message-inner">'+html+'</div></div>');
			}
		}
	});
}
function subscribe(id, type, z) {
	// id = unique id of the viewed profile
	// type = if is set, is an insert/delete type
	// z if on, activate the sublist class which sets another margin (friends dedicated profile page)
	
	if(z == 1) {
		$('#subscribe'+id).html('<div class="sub-loading subslist"></div>');
	} else {
		$('#subscribe'+id).html('<div class="sub-loading"></div>');
	}
	$.ajax({
		type: "POST",
		url: "requests/subscribe.php",
		data: "id="+id+"&type="+type+"&z="+z, 
		cache: false,
		success: function(html) {
			$('#subscribe'+id).html(html);
		}
	});
}
function deleteNotification(type, id) {
	if(type == 0) {
		$('#notification'+id).fadeOut(500, function() { $('#notification'+id).remove(); });
	} else if(type == 1) {
		$('#post_comment_'+id).fadeOut(500, function() { $('#post_comment_'+id).remove(); });
	}
}
function privacy(id, value) {
	// id = unique id of the message/comment
	// value = value to set on the post
	$('#privacy'+id).empty();
	$('#privacy'+id).html('<div class="privacy_loader"></div>');
	$.ajax({
		type: "POST",
		url: "requests/privacy.php",
		data: "message="+id+"&value="+value, 
		cache: false,
		success: function(html) {
			$('#privacy'+id).empty();
			if(html == 1) {
				if(value == 1) {
					var newVal = 0;
					var newClass = 'public';
					$('#comment_box_'+id).show('slow');
				} else if(value == 0) {
					var newVal = 1;
					var newClass = 'private';
					$('#comment_box_'+id).hide('slow');
				}
			$('#privacy'+id).html('<a onclick="privacy('+id+', '+newVal+')" title="This post is '+newClass+'"><div class="'+newClass+'_btn"></div></a>');
			}
		}
	});
}
function manage_the(start, type) {
	if(type == 1) {
		type = 'reports';
	} else {
		type = 'users';
	}
	$('#more_'+type).html('<div class="load_more"><div class="preloader-retina-large preloader-center"></div></div>');
	
	$.ajax({
		type: "POST",
		url: "requests/manage_"+type+".php",
		data: "start="+start, 
		cache: false,
		success: function(html) {
			$('#more_'+type).remove();
			
			// Append the new comment to the div id
			$('#'+type).append(html);
		}
	});
}
function delete_user(id) {
	// id = unique id of the message/comment
	// type = type of post: message/comment
	
	$('#user'+id).html('<div class="preloader-retina"></div>');
	
	$.ajax({
		type: "POST",
		url: "requests/delete_user.php",
		data: "id="+id, 
		cache: false,
		success: function(html) {
			if(html == '1') {
				$('#user'+id).fadeOut(500, function() { $('#message'+id).remove(); });
			} else {
				$('#user'+id).html('Sorry, but this user could not be deleted.');
			}
		}
	});
}
function manage_report(id, type, post, kind) {
	$('#report'+id).html('<div class="preloader-retina"></div>');
	
	$.ajax({
		type: "POST",
		url: "requests/manage_reports.php",
		data: "id="+id+"&type="+type+"&post="+post+"&kind="+kind, 
		cache: false,
		success: function(html) {
			if(html == '1') {
				$('#report'+id).fadeOut(500, function() { $('#message'+id).remove(); });
			} else {
				$('#report'+id).html('Sorry, but something went wrong, please refresh the page and try again.');
			}
		}
	});
}
function doLike(id, type) {
	// id = unique id of the message
	// type = 1 do the like, 2 do the dislike
	$('#like_btn'+id).html('<div class="privacy_loader"></div>');
	$('#doLike'+id).removeAttr('onclick');
	$.ajax({
		type: "POST",
		url: "requests/like.php",
		data: "id="+id+"&type="+type, 
		cache: false,
		success: function(html) {
			$('#message-action'+id).empty();
			$('#message-action'+id).html(html);
		}
	});
}
function doBlock(id, type) {
	// id = unique id of the message
	// type 0: do nothing, just display the block, type 1: do/undo block
	$('.blocked-button').html('<div class="privacy_loader"></div>');
	$.ajax({
		type: "POST",
		url: "requests/block.php",
		data: "id="+id+"&type="+type, 
		cache: false,
		success: function(html) {
			$('.blocked-button').html(html);
		}
	});
}
function showNotification(x, y) {
	// Y1: Show the global notifications
	// Y2: Show the messages notifications
	if(x == 'close') {
		$('.notification-container').hide();
		$('#messages_btn').removeClass('menu_hover_messages');
		$('#notifications_btn').removeClass('menu_hover_notifications');
		checkNewNotifications();
	} else {
		// Stop checking for new notifications while reading them
		clearTimeout(stopNotifications);
		
		$('.notification-container').show();
		if(y == 1) {
			$('#notifications_btn').addClass('menu_hover_notifications');
			$('#notifications_btn').html(getNotificationImage());
			
			// Remove the other hovered class if exist
			$('#messages_btn').removeClass('menu_hover_messages');
			
			// Show-Hide the top urls for global and chat messages drop-downs
			$('#global_page_url').show();
			$('#chat_page_url').hide();
		} else {
			$('#messages_btn').addClass('menu_hover_messages');
			$('#messages_btn').html(getMessagesImageUrl(1));
			
			// Remove the other hovered class if exist
			$('#notifications_btn').removeClass('menu_hover_notifications');
			
			// Show-Hide the top urls for global and chat messages drop-downs
			$('#global_page_url').hide();
			$('#chat_page_url').show();
			
			var extra = '&for=1';
		}
		$('#notifications-content').html('<div class="message-divider"></div><div class="notification-inner"><div class="preloader-normal"></div></div>');
		
		$.ajax({
			type: "POST",
			url: "requests/check_notifications.php",
			data: "type=1"+extra,
			cache: false,
			success: function(html) {
				if(html) {
					$('#notifications-content').html(html);
					jQuery("span.timeago").timeago();
				}
				if(extra) {
					$('#messages_url').removeAttr('onclick');
					$('#messages_url').attr('href', getMessagesImageUrl());
				}
			}
		});
	}
}
function startUpload() {
	document.getElementById("imageForm").target = "my_iframe"; //'my_iframe' is the name of the iframe
	document.getElementById("imageForm").submit();
	document.getElementById("post-loader9999999999").style.visibility = "visible";
}
function stopUpload(success){      
	document.getElementById("post-loader9999999999").style.visibility = "hidden";
	document.getElementById("load-content").innerHTML = success + document.getElementById("load-content").innerHTML;
	document.getElementById("imageForm").reset();
	document.getElementById("post9999999999").style.height = "38px";
	document.getElementById("queued-files").innerHTML = "0";
	// Reset the selected 'type' option
	$('#values label').addClass('selected').siblings().removeClass('selected');
	$('.message-form-input').hide('slow');
	jQuery("div.timeago").timeago();
	autosize();
	return true;   
}
function focus_form(id) {
	document.getElementById('comment-form'+id).focus();
	showButton(id);
}
function resizeGallery() {
	// image-container class
	var maxWidth = 1000;
	var maxHeight = 600;
	
	$('.image-container').css('max-width', maxWidth);
	$('.image-container').css('max-height', maxHeight);
	
	var currentWidth = $(window).width();
	var currentHeight = $(window).height();
	var currentMidWidth = Math.abs(currentWidth - maxWidth);
	var currentMidHeight = Math.abs(currentHeight - maxHeight);
	
	// Calculate the Width
	if(currentMidWidth <= 40 && currentMidWidth >= 0) {
		$('.image-container').css('max-width', currentWidth - 40);
		$('.image-container').css('margin-left', 20);
		$('.image-container').css('margin-right', 20);
	} else if(maxWidth < currentWidth) {
		$('.image-container').css('margin-left', ((currentWidth - maxWidth) / 2));
		$('.image-container').css('margin-right', ((currentWidth - maxWidth) / 2));
	} else {
		$('.image-container').css('max-width', currentWidth - 40);
	}
	
	// Calculate the Height
	if(currentMidHeight <= 40 && currentMidHeight >= 0) {
		$('.image-container').css('max-height', currentHeight - (62 - 20));
		$('.image-container').css('margin-top', 20);
		$('.image-container').css('margin-bottom', 20);
		$('.image-content').css('height', currentHeight - (40 + 62));
		$('#gallery-next, #gallery-prev').css({'height': ($('.image-content').height()-35), 'top': '35px'});
		// console.log('AAA');
	} else if(maxHeight < currentHeight) {
		$('.image-container').css('margin-top', ((currentHeight - maxHeight) / 2));
		$('.image-container').css('margin-bottom', ((currentHeight - maxHeight) / 2));
		$('.image-content').css('height', maxHeight - 62);
		$('#gallery-next, #gallery-prev').css({'height': ($('.image-content').height()-35), 'top': '35px'});
		// console.log('BBB');
	} else {
		$('.image-container').css('max-height', currentHeight - 40);
		$('.image-content').css('height', currentHeight - (40 + 62));
		$('#gallery-next, #gallery-prev').css({'height': ($('.image-content').height()-35), 'top': '35px'});
		// console.log('CCC');
	}
	
	// console.log('Image Width:'+$('img.ri').width());
	// console.log('Image Height:'+$('img.ri').height());
	// console.log('Container Width:'+$('div.image-content').width());
	// console.log('Container Height:'+$('div.image-content').height());
	return false;
	
	//$('.image-container');
}
function manageResults(x) {
	if(x == 0) {
		$(".search-container").hide();
		$(".search-content").remove();
	} else if(x == 1) {
		var q = $("#search").val();
		document.location='index.php?a=search&q='+escape(q.replace(' ','+'));
	} else if(x == 2) {
		var q = $("#search").val();
		document.location='index.php?a=search&tag='+escape(q.replace('#',''));
	}
}
function liveSearch() {
	var q = $('#search').val();
	
	// If the query starts with #, do not execute anything
	if(q == '#') {
		$(".search-container").hide();
		$(".search-content").remove();
		return false;
	}
	
	// Search if the hashtag is typed
	if(q.indexOf('#') === -1) {
		var y = 'q';
		var url = 'people';
		$('#search').keypress(function(x){if(x.keyCode==13){q=$(this).val();if(q!=this.defaultValue){document.location='index.php?a=search&'+y+'='+escape(q.replace(' ','+'))}}});
	} else {
		var y = 'tag';
		var url = 'tags';
		$('#search').keypress(function(x){if(x.keyCode==13){q=$(this).val();if(q!=this.defaultValue){document.location='index.php?a=search&'+y+'='+escape(q.replace('#',''))}}});
	}
	
	// If the text input is 0, remove everything instantly by setting the MS to 1
	if(q == 0) {
		var ms = 0;
	} else {
		$('.search-container').show();
		$('.search-container').html('<div class="search-content"><div class="search-results"><div class="message-inner"><div class="retrieving-results">Retrieving Results</div> <div class="preloader-retina preloader-left"></div></div></div></div>');
		var ms = 200;
	}
	
	// Start the delay (to prevent some useless queries)
	setTimeout(function() {
		if(q == $('#search').val()) {
			if(q == 0) {
				$(".search-container").hide();
				$(".search-content").remove();
			} else {
				$.ajax({
				type: "POST",
				url: "requests/load_"+url+".php",
				data: 'q='+q+'&start=1&live=1', // start is not used in this particular case, only needs to be set
				cache: false,
				success: function(html) {
					$(".search-container").html(html).show();
				}
				});
			}
		}
	}, ms);
	
}
function chatLiveSearch() {
	var q = $('#search-list').val();
	$('.sidebar-chat-list').empty();
	
	// If the text input is 0, remove everything instantly by setting the MS to 1
	
	$('.search-list-container').show();
	$('.search-list-container').html('<div class="search-content"><div class="message-inner"><div class="preloader-retina-large preloader-center"></div></div></div>');
	var ms = 200;
	
	// Start the delay (to prevent some useless queries)
	setTimeout(function() {
		if(q == $('#search-list').val()) {
			
			$.ajax({
				type: "POST",
				url: "requests/load_people.php",
				data: 'q='+q+'&start=1&live=1&list=1', // start is not used in this particular case, only needs to be set
				cache: false,
				success: function(html) {
					$('.search-list-container').html('');
					$('.sidebar-chat-list').html(html);
				}
			});
			
		}
	}, ms);
}
function profileCard(id, post, type, delay) {
	// ID: Unique user ID
	// Post: Unique Message/Post ID
	// Type: 0 - Message; 1 - Comment;
	// Delay: 0 - on mouse IN; 1 - on mouse OUT;
	if(delay == 1) {
		clearInterval(pcTimer);
	} else {
		pcTimer = setInterval(function(){
		if(type == 1) {
			var classType = 'comment';
			// The position to be increased
			var height = 45;
			var left = 0;
		} else {
			var classType = 'message';
			// The position to be increased
			var height = 58;
			var left = 20;
		}
		
		// Start displaying the profile card with the preloader
		$('#profile-card').show();
		$('#profile-card').html('<div class="profile-card-padding"><div class="preloader-retina preloader-center"></div></div>');
	
		// Get the position of the parent element
		var position = $("#"+classType+post).position();
		
		// Store the position into an array
		var pos = {
			top: (position.top + height) + 'px',
			left: (position.left + left) + 'px'
		};
		
		// Set the position of the profile card
		$('#profile-card').css(pos);
		$.ajax({
			type: "POST",
			url: "requests/load_profilecard.php",
			data: 'id='+id,
			cache: false,
			success: function(html) {			
				$('#profile-card').html(html);
			},
			error: function() {
				$('#profile-card').hide();
			}
		});
		clearInterval(pcTimer);
		}, 500);
	}
}
function notificationTitle(type) {
	// Type 1: Play the New Chat Message notification
	if(!document.hasFocus()) {
		if(type == 1) {
			$('#soundNewChat')[0].play();
		} else if(type == 2) {
			$("#soundNewNotification")[0].play();
		}
		
		// If the current document title doesn't have an alert, add one
		if(document.title.indexOf('(!)') == -1) {
			document.title = '(!) ' + document.title;
		}
	}
}
$(document).ready(function() {
	$('input#chat').bind('keydown', function(e) {
		if(e.keyCode==13) {
			// Store the message into var
			var message = $('input#chat').val();
			var id = $('#chat').attr('class');
			if(message) {
				// Remove chat errors if any
				$('.chat-error').remove();
				
				// Show the progress animation
				$('.message-loader').show();
				
				// Reset the chat input area			
				document.getElementById("chat").style.height = "25px";
				$('input#chat').val('');
				
				$.ajax({
					type: "POST",
					url: "requests/post_chat.php",
					data: 'message='+encodeURIComponent(message)+'&id='+id.replace('chat-user', ''),
					cache: false,
					success: function(html) {
						// Check if in the mean time any message was sent
						checkNewChat(1);
						
						// Append the new chat to the div chat container
						$('.chat-container').append(html);
						$('.message-loader').hide();
						
						jQuery("div.timeago").timeago();
						
						// Scroll at the bottom of the div (focus new content)
						$(".chat-container").scrollTop($(".chat-container")[0].scrollHeight);
					}
				});
			}
		}
	});
	
	$("#search").on('keyup', liveSearch);
	$("#search-list").on('keyup', chatLiveSearch);
	
	$(window).resize(function() {
		resizeGallery()
	});
	resizeGallery();
	$(".notification-close-info").click(function(){
		$(".notification-box-info").fadeOut("slow");return false;
	});
	 
	$(".notification-close-success").click(function(){
		$(".notification-box-success").fadeOut("slow");return false;
	});
	 
	$(".notification-close-warning").click(function(){
		$(".notification-box-warning").fadeOut("slow");return false;
	});
	 
	$(".notification-close-error").click(function(){
		$(".notification-box-error").fadeOut("slow");return false;
	});
	
	$(".close-transparent").click(function(){
		$(".box-transparent").fadeOut("slow");return false;
	});
	
	jQuery(".timeago").timeago();
	
	$('#gallery-close').click(function() {
		$("#gallery, .overall").fadeOut(300);
		return false;
	});
	
	$('#values input:radio').addClass('input_hidden');
	$('#values label').click(function() {
		$(this).addClass('selected').siblings().removeClass('selected');
		$('#form-value').attr("Placeholder", $(this).attr('title'));
		$('#form-value').val('');
		$('#my_file').val('');
		$('.message-form-input').show('slow');
		$('.selected-files').hide('slow');
	});
	
	$('#my_file').click(function() {
		$('#form-value').val('');
		$('.message-form-input').hide('slow');
		$('.selected-files').show('slow');
		$('#values label').removeClass('selected');
	});
	
	$(':file').change(function () {
		$('#queued-files').text(this.files.length);
	});
	
	// Disable the enter key on messages
	$('#imageForm').submit(function() {
		return false;
	});
	
	autosize();
	
	if($('#message-privacy').val() == 1) {
		$('.message-form-private').html('<div class="message-private-btn" id="privacy-btn"></div>');
		$('#privacy-btn').attr('title', 'Public message');
	} else {
		$('.message-form-private').html('<div class="message-private-btn message-private-active" id="privacy-btn"></div>');
		$('#privacy-btn').attr('title', 'Private message');
	}
	
	$('#privacy-btn').on('click', function() {
		if($('#message-privacy').val() == 1) {
			$('#message-privacy').val('0');
			$('#privacy-btn').addClass('message-private-active');
			$('#privacy-btn').attr('title', 'Private message');
		} else {
			$('#message-privacy').val('1');
			$('#privacy-btn').removeClass('message-private-active');
			$('#privacy-btn').attr('title', 'Public message');
		}
	});
	
	$('#profile-card').mouseleave(function() {
		$('#profile-card').hide();
	});
	
	// When the window is focused
	$(window).focus(function() {
		// If the currentTitle has the (!) notification, then remove it
		if(document.title.indexOf('(!)') >= 0) {
			document.title = document.title.replace("(!) ", "");
		}
	});
	
});
function gallery(id, uid, type) {
	// Show the Gallery
	$("#gallery, #gallery-background, .overall").fadeIn(300);
	
	// If the ID is close, close the Gallery
	if(id == 'close') {
		$("#gallery, .overall").fadeOut(300);
		return false;
	}
	
	// Escape the ID (contains dots) http://api.jquery.com/category/selectors/
	var parsedId = id.replace('.', '\\.');
	
	// Decide NEXT / PREV buttons
	var nextImg = ($('#'+parsedId).next('a'));
	var prevImg = ($('#'+parsedId).prev('a'));

	// If the ID attribute is undefined, hide the button
	if(!nextImg.attr('id')) {
		$('#gallery-next').hide();
	} else {
		$('#gallery-next').show();
		$('#gallery-next').attr('onclick', 'getNext(\''+id+'\', 0, '+uid+')');
	}
	if(!prevImg.attr('id')) {
		$('#gallery-prev').hide();
	} else {
		$('#gallery-prev').show();
		$('#gallery-prev').attr('onclick', 'getNext(\''+id+'\', 1, '+uid+')');
	}
	
	// Put the content
	$('.image-content').html('<img src="uploads/'+type+'/'+id+'" class="ri" />').fadeIn(300);
	$('.gallery-footer-container').html('<div class="message-avatar">'+$('#avatar'+uid).html()+'</div><div class="message-top"><a onclick="gallery(\'close\')" title="Close Gallery"><div class="delete_btn"></div></a><a href="uploads/'+type+'/'+id+'" title="Download Image" target="_blank"><div class="download_btn"></div></a><div class="message-author">'+$('#author'+uid).html()+'</div><div class="message-time">'+$('#time'+uid).html()+'</div></div>');
	jQuery('div.timeago').timeago();
	
	resizeGallery();
}
function getNext(currentId, direction, uid) {
	// Get the next id
	var parsedId = currentId.replace('.', '\\.');
	if(direction == 0) {
		var next = ($('#'+parsedId).next('a'));
	} else {
		var next = ($('#'+parsedId).prev('a'));
	}
	
	// Put the new Image
	$(".image-content").html('<img src="uploads/media/'+next.attr('id')+'" class="ri" />');
	$('.gallery-footer-container').html('<div class="message-avatar">'+$('#avatar'+uid).html()+'</div><div class="message-top"><a onclick="gallery(\'close\')" title="Close Gallery"><div class="delete_btn"></div></a><a href="uploads/media/'+next.attr('id')+'" title="Download Image" target="_blank"><div class="download_btn"></div></a><div class="message-author">'+$('#author'+uid).html()+'</div><div class="message-time">'+$('#time'+uid).html()+'</div></div>');
	jQuery('div.timeago').timeago();
	
	var currentId = next.attr('id').replace('.', '\\.');
	
	// Decide NEXT / PREV buttons
	var nextImg = ($('#'+currentId).next('a'));
	var prevImg = ($('#'+currentId).prev('a'));

	// If the ID attribute is undefined, hide the button
	if(!nextImg.attr('id')) {
		$('#gallery-next').hide();
	} else {
		$('#gallery-next').show();
		$('#gallery-next').attr('onclick', 'getNext(\''+next.attr('id')+'\', 0, '+uid+')');
	}
	if(!prevImg.attr('id')) {
		$('#gallery-prev').hide();
	} else {
		$('#gallery-prev').show();
		$('#gallery-prev').attr('onclick', 'getNext(\''+next.attr('id')+'\', 1, '+uid+')');
	}
	resizeGallery();
}