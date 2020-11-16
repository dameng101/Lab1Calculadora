

title "sample section"

control "rsch-1" do 
  impact 0.7 
  title "Connect to Research Source" 
  describe host(input('website_target'), port: 80, protocol: 'tcp') do
    it { should be_reachable }
  end
end