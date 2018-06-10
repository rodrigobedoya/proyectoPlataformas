$(window).load(function(){
			var i = 0;
			var images = ['image1.jpg','image2.jpg','image3.jpg'];
			var image = $('#slideit');
			image.css('background-image','url(/static/images/image1.jpg');
			setInterval(function(){
				image.fadeOut(1000,function(){
					image.css('background-image','url(/static/images/'+images[i++]+')');
					image.fadeIn(1000);
				});
				if(i==images.length)
					i = 0;
			},10000);
		});