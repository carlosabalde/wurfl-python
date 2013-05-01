<?php

require_once dirname ( __FILE__ ) . '/../classautoloader.php';

class WURFL_TestUtils_MockPersistenceProvider  {

	private $data;
	
	public  function __construct($datas) {
		$this->datas = $datas;
	}
	
	public function load($objectId){
		return $this->datas[$objectId];		
	}
	
}

