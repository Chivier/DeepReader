wget https://github.com/lxgw/LxgwZhenKai/releases/download/v0.704.1/LXGWZhenKai-Regular.ttf
wget https://github.com/lxgw/LxgwZhenKai/releases/download/v0.704.1/LXGWZhenKaiGB-Regular.ttf
wget https://github.com/lxgw/LxgwWenKai/releases/download/v1.511/LXGWWenKai-Light.ttf
wget https://github.com/lxgw/LxgwWenKai/releases/download/v1.511/LXGWWenKai-Medium.ttf
wget https://github.com/lxgw/LxgwWenKai/releases/download/v1.511/LXGWWenKai-Regular.ttf

mkdir -p ~/.local/share/fonts
mv LXGWZhenKai-Regular.ttf ~/.local/share/fonts/
mv LXGWZhenKaiGB-Regular.ttf ~/.local/share/fonts/
mv LXGWWenKai-Light.ttf ~/.local/share/fonts/
mv LXGWWenKai-Medium.ttf ~/.local/share/fonts/
mv LXGWWenKai-Regular.ttf ~/.local/share/fonts/

fc-cache -fv