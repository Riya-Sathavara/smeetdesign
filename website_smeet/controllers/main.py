from openerp import http
from openerp.http import request


class website_smeet(http.Controller):


    @http.route(['/page/about'], type='http', auth="public", website=True)
    def about(self, **post):
        return request.website._render("website_smeet.website_smeets_about", {})
    
    @http.route(['/page/news'], type='http', auth="public", website=True)
    def news(self, **post):
        return request.website._render("website_smeet.website_smeets_news_page", {})
    
    @http.route(['/page/newsdetail/1'], type='http', auth="public", website=True)
    def newsdetail1(self, **post):
        return request.website._render("website_smeet.website_smeets_news_detail_1", {})
    
    @http.route(['/page/newsdetail/2'], type='http', auth="public", website=True)
    def newsdetail2(self, **post):
        return request.website._render("website_smeet.website_smeets_news_detail_2", {})
    
    @http.route(['/page/newsdetail/3'], type='http', auth="public", website=True)
    def newsdetail3(self, **post):
        return request.website._render("website_smeet.website_smeets_news_detail_3", {})
    
    @http.route(['/page/product/1'], type='http', auth="public", website=True)
    def product1(self, **post):
        return request.website._render("website_smeet.website_smeets_product_1", {})
    
    @http.route(['/page/product/2'], type='http', auth="public", website=True)
    def product2(self, **post):
        return request.website._render("website_smeet.website_smeets_product_2", {})
    
    @http.route(['/page/product/3'], type='http', auth="public", website=True)
    def product3(self, **post):
        return request.website._render("website_smeet.website_smeets_product_3", {})
    
    @http.route(['/page/product/4'], type='http', auth="public", website=True)
    def product4(self, **post):
        return request.website._render("website_smeet.website_smeets_product_4", {})
    
    @http.route(['/page/product/5'], type='http', auth="public", website=True)
    def product5(self, **post):
        return request.website._render("website_smeet.website_smeets_product_5", {})
    
    @http.route(['/page/product/6'], type='http', auth="public", website=True)
    def product6(self, **post):
        return request.website._render("website_smeet.website_smeets_product_6", {})
    
    #     @http.route(['/page/product'], type='http', auth="public", website=True)
#     def product(self, **post):
#         return request.website._render("smeets_trading_theme.product", {})
# 
#     @http.route(['/page/news'], type='http', auth="public", website=True)
#     def news(self, **post):
#         return request.website._render("smeets_trading_theme.news", {})
# 
#     @http.route(['/page/blog_page'], type='http', auth="public", website=True)
#     def blog_page(self, **post):
#         return request.website._render("smeets_trading_theme.read_more_blog", {})

    
    
    
