require "net/http"
require "net/https"
require "uri"
require 'json'

tags = {
	# "Dev Smoke" => "SOMEORG-RCWAT",
	# "Dev Retail" => "SOMEORG-RCWAT3",
	# "Dev Corp" => "SOMEORG-RCWAT0",
	# "Dev Elevate" => "SOMEORG-RCWAT17",
	# "Dev Inc" => "SOMEORG-RCWAT21",
	"SIT Retail" => "SOMEORG-RCWAT4",
	"SIT Corp" => "SOMEORG-RCWAT5",
	"SIT Inc" => "SOMEORG-RCWAT23",
	"SIT Elevate" => "SOMEORG-RCWAT19"
}


def get_bamboo_result(uri)
	proxy_addr="ausydisa02.au.imckesson.com"
	proxy_port=8080

	begin
		http = Net::HTTP.new(uri.host, uri.port, proxy_addr, proxy_port)
		http.use_ssl = true
		http.verify_mode = OpenSSL::SSL::VERIFY_NONE

		request = Net::HTTP::Get.new(uri.request_uri)
		response = http.request(request)
		return JSON.parse(response.body)["successful"]
	rescue => e
		puts e
		return nil
	end
end

def set_light(current_colour, new_colour)
	turn_off_lights # Blink health check

	scroll_lights if current_colour!=new_colour

	case new_colour 
	when :green
		update_device_config([0,0,1])
	when :yellow
		update_device_config([0,1,0])
	when :red
		update_device_config([1,0,0])
	end
end

def play_sound(current_colour, new_colour)
	if (current_colour==:red && new_colour==:green)
		`aplay red_to_green.wav`
	elsif (current_colour==:green && new_colour==:red)
		`aplay green_to_red.wav`
	end
end

def turn_off_lights
	update_device_config([0,0,0])
end

def scroll_lights 
	2.times do 
		update_device_config([1,0,0])
		update_device_config([0,1,0])
		update_device_config([0,0,1])
	end
end

def update_device_config(config)
	`./clewarecontrol -d 901880 -c 1 -as 0 #{config[0]} -as 1 #{config[1]} -as 2 #{config[2]}`
end

current_colour=:red
new_colour=nil

while true
	all_jobs_success=true

	tags.map do |env, tag|
		uri = URI.parse "https://bamboo-corp.dev.someorg.com.au/rest/api/latest/result/#{tag}/latest.json"
		job_success=get_bamboo_result(uri)
		puts "#{Time.now} env: #{env} tag: #{tag} success: #{job_success}"
		if job_success == nil 	 
			new_colour = :yellow
			all_jobs_success=false
		elsif job_success==false
			new_colour = :red
			all_jobs_success=false
		end
	end

	new_colour = :green if all_jobs_success

	set_light(current_colour, new_colour)
	play_sound(current_colour, new_colour)

	current_colour=new_colour

	sleep(30)
end
