\o nome.sql


select 
    'update fashion_form set base_name = ''' || pt.name || ''' where id = ' || ff.id || ';' 
from fashion_form ff 
    join fashion_form ffb on (ff.base_id = ffb.id) 
    join product_template pt on (ffb.product_id = pt.id);
    
    
    
\i nome.sql
    
